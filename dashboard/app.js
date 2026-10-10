/* A dependency-free view over Python-generated scores; no data is fetched live. */
'use strict';
const data = window.CITYINSIGHT_DATA;
const dims = ['economy', 'cost', 'service', 'environment'];
const dimNames = {economy:'经济机会',cost:'生活成本',service:'公共服务',environment:'环境质量'};
const indicatorNames = {gdp_per_capita:'人均 GDP',avg_salary_non_private:'非私营单位年均工资',avg_salary_private:'私营单位年均工资',tertiary_industry_ratio:'第三产业占比',house_price:'二手住宅样本均价',rent_per_sqm:'住宅租金单价',house_price_income_ratio_non_private:'房价收入比 · 非私营',house_price_income_ratio_private:'房价收入比 · 私营',hospital_count:'医院数量',university_count:'普通高校数量',rail_station_count:'城轨车站数（换乘去重）',pm25:'PM2.5 年均浓度',good_air_days_ratio:'空气优良天数比例',park_count:'公园数量'};
const presets = {balanced:[35,30,20,15],career:[55,20,15,10],budget:[20,55,15,10],green:[20,20,20,40]};
const el = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = (value, digits=1) => value == null ? '—' : Number(value).toLocaleString('zh-CN',{maximumFractionDigits:digits,minimumFractionDigits:digits});
let currentWeights = [...presets.balanced];
const years = [...new Set(data.cities.map(c=>c.year))].sort((a,b)=>b-a);
el('year').innerHTML = years.map(y=>`<option value="${y}">${y}</option>`).join('');
const yearRows = () => data.cities.filter(c=>c.year===Number(el('year').value));
const normalizedWeights = () => currentWeights.map(w=>w/currentWeights.reduce((a,b)=>a+b,0));
function currentCities() {
  const weights = normalizedWeights();
  const rows = yearRows().map(c=>({...c,custom_score:c.status==='provisional' ? Math.round(dims.reduce((sum,d,i)=>sum+c[d+'_score']*weights[i],0)*10)/10 : null}));
  rows.forEach(c=>{c.custom_rank = c.custom_score==null ? null : 1+rows.filter(other=>other.custom_score!=null && other.custom_score>c.custom_score).length;});
  return rows;
}
function updateWeights() {
  const weights = normalizedWeights();
  dims.forEach((d,i)=>el('output-'+d).textContent=number(weights[i]*100,1)+'%');
  renderRanking(); renderCompare();
}
function setPreset(name) {
  currentWeights=[...presets[name]];
  dims.forEach((d,i)=>el('weight-'+d).value=currentWeights[i]);
  document.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('selected',b.dataset.preset===name));
  el('weight-status').textContent=''; updateWeights();
}
el('sliders').innerHTML = dims.map((d,i)=>`<div class="slider"><label for="weight-${d}">${dimNames[d]}<output id="output-${d}" for="weight-${d}">${currentWeights[i]}%</output></label><input type="range" id="weight-${d}" min="0" max="100" step="1" value="${currentWeights[i]}"></div>`).join('');
dims.forEach((d,i)=>el('weight-'+d).addEventListener('input',event=>{
  const trial=[...currentWeights]; trial[i]=Number(event.target.value);
  if(trial.every(w=>w===0)){event.target.value=currentWeights[i];el('weight-status').textContent='至少保留一个大于零的权重。';return;}
  currentWeights=trial;el('weight-status').textContent='';document.querySelectorAll('[data-preset]').forEach(b=>b.classList.remove('selected'));updateWeights();
}));
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>setPreset(b.dataset.preset)));
el('reset').addEventListener('click',()=>setPreset('balanced'));
function renderRanking() {
  const all=currentCities();
  const rows=all.filter(c=>c.city_name.includes(el('city-search').value.trim()));
  const sort=el('sort').value;
  rows.sort((a,b)=>sort==='coverage' ? b.coverage-a.coverage || a.city_id-b.city_id : sort==='name' ? a.city_name.localeCompare(b.city_name,'zh-CN') : (b.custom_score??-1)-(a.custom_score??-1)||a.city_id-b.city_id);
  const cohort=all.filter(c=>c.status==='provisional');
  el('stats').innerHTML=[[String(all.length).padStart(2,'0'),'研究样本城市'],[String(cohort.length).padStart(2,'0'),'暂定排名城市'],['04','评价维度'],[String(data.sources.filter(s=>Number(s.year)===Number(el('year').value)).length),'可追溯指标记录']].map(([n,label])=>`<div class="stat"><strong>${n}</strong><span>${label}</span></div>`).join('');
  el('ranking-list').innerHTML=rows.length ? rows.map(c=>`<article class="city-row"><span class="rank">${c.custom_rank==null?'·':String(c.custom_rank).padStart(2,'0')}</span><div class="city-name">${esc(c.city_name)}<small>${esc(c.province)} · ${number(c.coverage*100,0)}% 数据</small></div>${c.custom_score==null ? '<div class="unranked">数据待补齐 · 暂不参与综合排名</div>' : `<div class="mini-bars">${dims.map(d=>`<div>${dimNames[d]} ${number(c[d+'_score'],0)}<div class="track"><i style="width:${c[d+'_score']}%"></i></div></div>`).join('')}</div>`}<div class="score">${number(c.custom_score)}<small>${c.custom_score==null?'待补齐':'暂定分 / 100'}</small></div></article>`).join('') : '<p class="empty">没有匹配的城市。试试其他名称。</p>';
  const meta=data.cohorts[String(el('year').value)];
  el('cohort-note').textContent=`比较组：${cohort.map(c=>c.city_name).join('、')||'暂无'}。共同指标：${meta?dims.map(d=>`${dimNames[d]} ${meta.indicators[d].length} 项`).join(' / '):'暂无'}。筛选仅改变显示，评分基准保持固定。`;
}
function populateSelectors() {
  const rows=yearRows();
  for(const id of ['city-a','city-b','source-city']) {
    const old=el(id).value;
    el(id).innerHTML=(id==='source-city'?'<option value="all">全部城市</option>':'')+rows.map(c=>`<option value="${c.city_id}">${esc(c.city_name)}</option>`).join('');
    if([...el(id).options].some(o=>o.value===old))el(id).value=old;
  }
  if(el('city-a').value===el('city-b').value && rows.length>1)el('city-b').value=rows[1].city_id;
}
function radar(a,b) {
  if(a.custom_score==null||b.custom_score==null)return '<div class="empty"><h3>原始指标仍可对比</h3><p>至少一座城市的数据不足。补齐生活成本等维度后，才能生成可比的综合画像。</p></div>';
  const points=(values)=>values.map((v,i)=>{const angle=-Math.PI/2+i*Math.PI/2;return `${170+Math.cos(angle)*v*1.05},${145+Math.sin(angle)*v*1.05}`;}).join(' ');
  return `<svg class="radar" viewBox="0 0 340 310" role="img" aria-label="${esc(a.city_name)}与${esc(b.city_name)}四维度画像"><g fill="none" stroke="#e1e8df">${[25,50,75,100].map(n=>`<polygon points="${points([n,n,n,n])}"/>`).join('')}</g><polygon points="${points(dims.map(d=>a[d+'_score']))}" fill="#176c5025" stroke="#176c50" stroke-width="2"/><polygon points="${points(dims.map(d=>b[d+'_score']))}" fill="#bc8a4020" stroke="#bc8a40" stroke-width="2" stroke-dasharray="5 3"/><g fill="#69796f" font-size="11" text-anchor="middle"><text x="170" y="23">经济机会</text><text x="302" y="148">生活成本</text><text x="170" y="268">公共服务</text><text x="37" y="148">环境质量</text></g><g font-size="12" text-anchor="middle"><text x="115" y="300" fill="#176c50">● ${esc(a.city_name)}</text><text x="225" y="300" fill="#bc8a40">● ${esc(b.city_name)}</text></g></svg>`;
}
function renderCompare() {
  const rows=currentCities(),a=rows.find(c=>c.city_id===Number(el('city-a').value)),b=rows.find(c=>c.city_id===Number(el('city-b').value));
  if(!a||!b)return;
  const metricRows=[['偏好综合分',a.custom_score,b.custom_score,'分'],...dims.map(d=>[dimNames[d],a[d+'_score'],b[d+'_score'],'分']),...data.raw_indicators.map(col=>[indicatorNames[col],a[col],b[col],data.units[col]])];
  el('compare-content').innerHTML=`<div class="compare-grid">${radar(a,b)}<div class="table-wrap"><table><caption class="sr-only">城市得分和原始指标对比</caption><thead><tr><th>指标</th><th>${esc(a.city_name)}</th><th>${esc(b.city_name)}</th></tr></thead><tbody>${metricRows.map(([label,av,bv,unit])=>`<tr><td>${esc(label)}<small>${esc(unit)}</small></td><td>${number(av)}</td><td>${number(bv)}</td></tr>`).join('')}</tbody></table></div></div>`;
}
function sourceURL(value) {
  try {const url=new URL(value);return ['https:','http:'].includes(url.protocol) ? url.href : null;} catch{return null;}
}
function renderSources() {
  const city=yearRows().find(c=>c.city_id===Number(el('source-city').value));
  const sources=data.sources.filter(s=>Number(s.year)===Number(el('year').value)&&(!city||s.city===city.city_name));
  el('sources-body').innerHTML=sources.map(s=>{const url=sourceURL(s.source_url),verified=s.verification_status==='verified';return `<tr><td><strong>${esc(s.city)}</strong><small>${esc(indicatorNames[s.indicator]||s.indicator)}</small></td><td>${number(Number(s.value),1)}<small>${esc(s.unit)}</small></td><td>${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(s.source_name)} ↗</a>`:esc(s.source_name)}</td><td><span class="${verified?'verified':'pending'}">${verified?'已核对公开来源':'历史记录 · 待复核'}${s.verified_on?' · '+esc(s.verified_on):''}</span><small>${esc(s.notes)}</small></td></tr>`;}).join('')||'<tr><td colspan="4">暂无有值的来源记录。</td></tr>';
}
el('city-search').addEventListener('input',renderRanking);el('sort').addEventListener('change',renderRanking);
for(const id of ['city-a','city-b'])el(id).addEventListener('change',renderCompare);
el('source-city').addEventListener('change',renderSources);
el('year').addEventListener('change',()=>{populateSelectors();renderRanking();renderCompare();renderSources();});
el('download').addEventListener('click',()=>{
  const header=['城市','年份','暂定排名','偏好综合分','经济机会','生活成本','公共服务','环境质量','覆盖率','状态',...dims.map(d=>dimNames[d]+'权重')];
  const weights=normalizedWeights();
  const rows=currentCities().sort((a,b)=>(a.custom_rank??999)-(b.custom_rank??999)||a.city_id-b.city_id).map(c=>[c.city_name,c.year,c.custom_rank,c.custom_score,...dims.map(d=>c[d+'_score']),c.coverage,c.status,...weights]);
  const csv='\uFEFF'+[header,...rows].map(row=>row.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download=`cityinsight-${el('year').value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
populateSelectors();updateWeights();renderSources();
