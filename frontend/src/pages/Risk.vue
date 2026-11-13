<script setup lang="ts">import {ref,computed,watch} from 'vue';import type {Workspace} from '../stores/workspace';import type {Run,RiskAnalysis} from '../types/domain';import PageHeading from '../components/common/PageHeading.vue';import Notice from '../components/common/Notice.vue';import Empty from '../components/common/Empty.vue';import {create} from '../api/risk';import {useAsync} from '../hooks/useAsync';import {date} from '../utils/format';const MAX_GROUPS=12;const STATE_PREVIEW=20;const props=defineProps<{data:Workspace;canWrite:boolean;refresh:()=>Promise<void>}>();const selectedRun=ref('');const selectedAnalysis=ref('');const analysisName=ref('');const targetInput=ref('');const groups=ref<{name:string;probability:string;arc_ids:string[]}[]>([{name:'',probability:'',arc_ids:[]}]);const {busy,error,execute}=useAsync();const completedRuns=computed(()=>props.data.runs.filter(r=>r.status==='completed'));const run=computed<Run|undefined>(()=>completedRuns.value.find(r=>r.id===selectedRun.value)||completedRuns.value[0]);watch(()=>run.value?.id,()=>{selectedAnalysis.value='';analysisName.value='';targetInput.value='';groups.value=[{name:'',probability:'',arc_ids:[]}]});const snapshotArcs=computed(()=>(run.value?.result?.arcs||[]).slice().sort((a,b)=>a.arc_id.localeCompare(b.arc_id)));const analyses=computed<RiskAnalysis[]>(()=>props.data.riskAnalyses.filter(a=>a.run_id===run.value?.id));const current=computed<RiskAnalysis|undefined>(()=>analyses.value.find(a=>a.id===selectedAnalysis.value)||analyses.value[0]);const scenarioName=(id:string)=>props.data.scenarios.find(s=>s.id===id)?.name||'—';function addGroup(){if(groups.value.length<MAX_GROUPS)groups.value.push({name:'',probability:'',arc_ids:[]})}function removeGroup(i:number){groups.value.splice(i,1)}const pct=(v:number)=>((v*100).toFixed(2).replace(/\.?0+$/,''))+'%';const prob=(v:number)=>v.toFixed(4).replace(/0+$/,'').replace(/\.$/,'');
function validate():{name:string;probability:number;arc_ids:string[]}[]|string{
 if(!analysisName.value.trim())return '请填写分析名称';
 const target=Number(targetInput.value);
 if(!Number.isInteger(target)||target<0)return '目标箱量须为非负整数';
 if(!groups.value.length)return '至少填写一个风险组';
 const seen=new Set<string>();
 for(const g of groups.value){
  if(!g.name.trim())return '每个风险组都需要名称';
  if(seen.has(g.name.trim()))return '风险组名称重复：'+g.name.trim();
  seen.add(g.name.trim());
  const p=Number(g.probability);
  if(!Number.isFinite(p)||p<0||p>1)return `风险组「${g.name.trim()}」的故障概率须为0到1之间的数值`;
  if(!g.arc_ids.length)return `风险组「${g.name.trim()}」至少选择一条边`;
 }
 return groups.value.map(g=>({name:g.name.trim(),probability:Number(g.probability),arc_ids:g.arc_ids}));
}
async function submit(){
 await execute(async()=>{
  const v=validate();
  if(typeof v==='string')throw new Error(v);
  await create({run_id:run.value?.id,name:analysisName.value.trim(),target_throughput:Number(targetInput.value),groups:v});
  analysisName.value='';targetInput.value='';groups.value=[{name:'',probability:'',arc_ids:[]}];
  await props.refresh();
 });
}
</script>
<template><PageHeading code="06 / RAIN RISK GROUPS" title="雨灾故障组：精确枚举吞吐分布。" description="沿用当次推演的停边与边快照。同组边一起失效、组间相互独立，同一边可属多组；超过12组拒绝分析。"/>
 <section class="paper"><h2>选择已完成推演</h2>
  <div class="run-selector"><label>推演记录<select aria-label="选择推演记录" :value="run?.id" @change="selectedRun=($event.target as HTMLSelectElement).value;selectedAnalysis=''"><option v-for="r in completedRuns" :key="r.id" :value="r.id">{{scenarioName(r.scenario_id)}} · {{r.created_at.slice(11,19)}}</option></select></label></div>
  <Empty v-if="!run">没有已完成的推演，请先在“停用方案”运行并等待计算完成，再录入雨灾风险组。</Empty>
  <template v-else><p class="caption">快照校验码 {{run.result.checksum.slice(0,24)}}；当次停用边：{{run.result.disabled_arc_ids.length?run.result.disabled_arc_ids.join('、'):'无'}}；停用方案当前最大流 {{run.result.outage.max_flow.value}} 箱/小时。后续网络变化不会改动已保存的风险结果。</p></template>
 </section>
 <template v-if="run">
 <section class="paper" v-if="canWrite"><div class="section-heading"><h2>录入风险组</h2><span>同组一起失效 · 组间独立 · 一边可属多组 · 上限{{MAX_GROUPS}}组</span></div>
  <form class="grid-form" @submit.prevent="submit">
   <label>分析名称<input aria-label="分析名称" required minlength="1" v-model="analysisName" placeholder="如：汛期三场雨带"/></label>
   <label>目标箱量 / 箱每小时<input aria-label="目标箱量" required inputmode="numeric" pattern="[0-9]+" v-model="targetInput" :placeholder="'参考值 '+run.result.outage.max_flow.value"/></label>
  </form>
  <div class="risk-group-editor">
   <article class="risk-group-card" v-for="(g,i) in groups" :key="i">
    <div class="risk-group-head"><b>风险组 {{i+1}}</b><button type="button" class="text-button" :disabled="groups.length===1" @click="removeGroup(i)">移除</button></div>
    <div class="risk-group-fields"><label>组名<input v-model="g.name" :aria-label="'第'+(i+1)+'组名称'" placeholder="如：北岸雨带" required/></label>
    <label>故障概率 0–1<input v-model="g.probability" :aria-label="'第'+(i+1)+'组故障概率'" inputmode="decimal" placeholder="如 0.25" required/></label></div>
    <fieldset><legend>组内边ID（同组一起失效）</legend><div class="outage-checks">
     <label v-for="a in snapshotArcs" :key="a.arc_id"><input type="checkbox" :value="a.arc_id" v-model="g.arc_ids" :aria-label="g.name+(' 停用 '+a.arc_id)"/><span><b>{{a.arc_id}}</b> {{a.source}}→{{a.target}}<small>{{a.capacity}}箱/小时 · {{a.travel_minutes}}分钟</small></span></label>
    </div></fieldset>
   </article>
  </div>
  <div class="risk-actions"><button type="button" class="secondary" :disabled="busy||groups.length>=MAX_GROUPS" @click="addGroup">+ 增加风险组（{{groups.length}}/{{MAX_GROUPS}}）</button>
   <button :disabled="busy" @click="submit">精确枚举并保存分析</button></div>
  <Notice v-if="error" error>{{error}}</Notice>
  <p class="caption">共枚举 2^组数个故障状态：组内边同时失效，各组独立取故障/正常；未知边ID、非法概率或超过{{MAX_GROUPS}}组将整单拒绝。零概率与必然故障（概率0或1）同样逐状态计入。</p>
 </section>
 <section class="paper"><div class="section-heading"><h2>已保存的风险分析</h2><span>冻结于当次快照，网络后续变化不改旧结果</span></div>
  <Empty v-if="!analyses.length">还没有风险分析记录。</Empty>
  <template v-else>
   <div class="run-selector"><label>查看记录<select aria-label="选择风险分析" :value="current?.id" @change="selectedAnalysis=($event.target as HTMLSelectElement).value"><option v-for="a in analyses" :key="a.id" :value="a.id">{{a.name}} · 目标{{a.target_throughput}}箱 · {{a.created_at.slice(11,19)}}</option></select></label></div>
   <article v-if="current" class="risk-result">
    <div class="risk-summary">
     <div><small>目标箱量达标概率（吞吐 ≥ {{current.target_throughput}}）</small><b>{{pct(current.result.target_probability)}}</b></div>
     <div><small>期望吞吐 / 箱每小时</small><b>{{current.result.expected_throughput.toFixed(3)}}</b></div>
     <div><small>快照参考吞吐 / 箱每小时</small><b>{{current.result.reference_throughput}}</b></div>
     <div><small>概率总和（须为1）</small><b>{{prob(current.result.probability_sum)}}</b></div>
    </div>
    <p class="caption">由 {{current.created_by}} 保存于 {{date(current.created_at)}}；{{current.result.group_count}}个风险组精确枚举{{current.result.state_count}}个状态，合并为{{current.result.distinct_throughput_count}}档吞吐；实际最大流计算{{current.result.maxflow_call_count}}次（相同失效集合去重）。</p>
    <p class="caption" v-if="current.result.zero_probability_groups.length||current.result.deterministic_failure_groups.length">零概率组：{{current.result.zero_probability_groups.join('、')||'无'}}；必然故障组：{{current.result.deterministic_failure_groups.join('、')||'无'}}（对应状态仍逐一枚举，零概率档位概率记0）。</p>
    <h3>吞吐分布（相同吞吐已合并）</h3>
    <div class="table-scroll"><table><thead><tr><th>吞吐 / 箱每小时</th><th>概率</th><th>占比</th><th>合并状态数</th><th>失效组组合</th></tr></thead><tbody>
     <tr v-for="b in current.result.distribution" :key="b.throughput"><td><b>{{b.throughput}}</b></td><td>{{prob(b.probability)}}</td><td><div class="prob-bar"><i :style="{width:pct(b.probability)}"></i><span>{{pct(b.probability)}}</span></div></td><td>{{b.state_count}}</td><td><span class="tag" v-for="s in b.states.slice(0,STATE_PREVIEW)" :key="s.failed_group_names.join('+')||'none'">{{s.failed_group_names.length?s.failed_group_names.join('+'):'全组正常'}} · {{prob(s.probability)}}</span><small v-if="b.states.length>STATE_PREVIEW">其余 {{b.states.length-STATE_PREVIEW}} 个状态同吞吐，已合并计入口径概率</small></td></tr>
    </tbody></table></div>
    <h3>风险组台账</h3>
    <div class="table-scroll"><table><thead><tr><th>风险组</th><th>故障概率</th><th>边ID（同组一起失效）</th></tr></thead><tbody>
     <tr v-for="g in current.groups" :key="g.name"><td><b>{{g.name}}</b></td><td>{{prob(g.probability)}}</td><td><span class="tag" v-for="id in g.arc_ids" :key="id">{{id}}</span></td></tr>
    </tbody></table></div>
   </article>
  </template>
 </section>
 </template>
</template>
