from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from plotly.offline.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'WA_Fn-UseC_-HR-Employee-Attrition.csv'
OUT = ROOT / 'results'
IMAGES = ROOT / 'images'
DASH = ROOT / 'dashboard'


def main():
    if not DATA.exists():
        raise FileNotFoundError(f'Dataset missing: {DATA}')
    for folder in [OUT, IMAGES, DASH]: folder.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    required = {'EmployeeNumber','Attrition','Age','Department','JobRole','OverTime','Gender','MonthlyIncome','JobSatisfaction'}
    if missing := required - set(df.columns):
        raise ValueError(f'Missing dataset columns: {sorted(missing)}')
    df['AttritionFlag'] = df['Attrition'].eq('Yes').astype(int)
    df['AgeGroup'] = pd.cut(df['Age'], bins=[0,25,35,45,55,200], labels=['25 or younger','26–35','36–45','46–55','56+'], include_lowest=True).astype(str)
    df['IncomeGroup'] = pd.cut(df['MonthlyIncome'], bins=[-1,3000,6000,10000,float('inf')], labels=['Up to 3,000','3,001–6,000','6,001–10,000','Over 10,000']).astype(str)
    df.to_csv(OUT/'hr_powerbi_ready.csv', index=False)
    fields = [('Department','department'),('JobRole','job_role'),('OverTime','overtime'),('AgeGroup','age_group'),('IncomeGroup','income_group'),('JobSatisfaction','job_satisfaction'),('Gender','gender')]
    for field, name in fields:
        g = df.groupby(field, dropna=False, observed=True).agg(employees=('EmployeeNumber','nunique'),left=('AttritionFlag','sum')).reset_index()
        g['attrition_rate_pct'] = (100*g['left']/g['employees']).round(2)
        g.to_csv(OUT/f'attrition_by_{name}.csv', index=False)
    total = df.EmployeeNumber.nunique(); left = int(df.AttritionFlag.sum()); rate = left/total*100
    summary = {'total_employees':total,'employees_left':left,'employees_remaining':total-left,'attrition_rate_pct':round(rate,2),'average_monthly_income':round(float(df.MonthlyIncome.mean()),2)}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (OUT/'summary.txt').write_text('\n'.join(f'{k}: {v}' for k,v in summary.items())+'\n',encoding='utf-8')
    for field, name in fields[:6]:
        g = df.groupby(field, observed=True).agg(employees=('EmployeeNumber','nunique'),left=('AttritionFlag','sum')).reset_index()
        g['rate'] = g.left/g.employees*100
        g = g.sort_values('rate')
        fig,ax=plt.subplots(figsize=(10,5.5))
        ax.barh(g[field].astype(str),g['rate'],color='#2563eb')
        ax.set_xlabel('Attrition rate (%)'); ax.set_title('Attrition Rate by '+field.replace('Group',' Group'))
        ax.grid(axis='x',alpha=.18)
        fig.tight_layout();fig.savefig(IMAGES/f'attrition_by_{name}.png',dpi=150);plt.close(fig)
    cols=['EmployeeNumber','AttritionFlag','Department','JobRole','OverTime','Gender','AgeGroup','IncomeGroup','JobSatisfaction','MonthlyIncome','Age']
    records=df[cols].where(pd.notna(df[cols]),None).to_dict(orient='records')
    html=HTML_TEMPLATE.replace('/*PLOTLY_LIBRARY*/',get_plotlyjs()).replace('/*DATA_RECORDS*/',json.dumps(records,ensure_ascii=False,default=str))
    (DASH/'HR_Analytics_Dashboard.html').write_text(html,encoding='utf-8')
    print(f'SUCCESS: {total:,} employees; {left:,} left ({rate:.1f}%).')
    print('Open dashboard/HR_Analytics_Dashboard.html in your browser.')
    print('Charts in images/; CSV reports and Power BI-ready data in results/.')

HTML_TEMPLATE=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR Analytics | Employee Attrition</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fb;color:#17243d;font:15px 'Segoe UI',Arial,sans-serif}.shell{max-width:1450px;margin:auto;padding:28px 32px}.head{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:22px}.eyebrow{font-size:11px;letter-spacing:2.5px;font-weight:800;color:#4478c8}h1{margin:6px 0 5px;font-size:30px;letter-spacing:-.8px}p{margin:0;color:#66758b}.pill{border:1px solid #dce5f2;background:#fff;border-radius:50px;padding:10px 15px;font-size:12px;color:#54657c}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.filter{background:white;border:1px solid #e2e9f2;border-radius:10px;padding:9px 13px;min-width:175px;flex:1}.filter label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:#78879a;font-weight:700;margin-bottom:5px}select{width:100%;border:0;background:transparent;font:14px 'Segoe UI',Arial;color:#1a2b46;outline:0}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.kpi,.panel{background:#fff;border:1px solid #e5ebf3;border-radius:15px;box-shadow:0 5px 20px #1e37620a}.kpi{padding:22px 24px;border-top:3px solid #2563eb}.kpi:nth-child(2){border-top-color:#f97373}.kpi:nth-child(3){border-top-color:#19a68c}.kpi:nth-child(4){border-top-color:#8058d8}.kpi .label{font-size:12px;color:#687990;font-weight:600}.kpi .value{font-size:33px;font-weight:800;letter-spacing:-1px;margin-top:8px}.kpi .sub{font-size:11px;color:#91a0b2;margin-top:4px}.charts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:18px}.panel{padding:19px 18px 8px;min-width:0}.panel h2{font-size:15px;margin:0 0 1px 6px}.panel p{font-size:11px;margin:0 0 0 6px}.plot{height:305px}.foot{margin:22px 0;color:#7b8ba0;font-size:12px;line-height:1.6}@media(max-width:850px){.kpis{grid-template-columns:repeat(2,1fr)}.charts{grid-template-columns:1fr}.shell{padding:16px}}@media(max-width:480px){.kpis{grid-template-columns:1fr}}
</style><script>/*PLOTLY_LIBRARY*/</script></head><body><main class="shell"><div class="head"><div><div class="eyebrow">WORKFORCE INTELLIGENCE / HR ANALYTICS</div><h1>Employee Attrition Dashboard</h1><p>IBM HR Analytics dataset · Interactive employee retention insights</p></div><div class="pill">● Local interactive report</div></div>
<div class="filters"><div class="filter"><label>Department</label><select id="department"><option value="">All departments</option></select></div><div class="filter"><label>Gender</label><select id="gender"><option value="">All genders</option></select></div><div class="filter"><label>Overtime</label><select id="overtime"><option value="">All employees</option></select></div><div class="filter"><label>Job role</label><select id="role"><option value="">All job roles</option></select></div></div>
<section class="kpis"><div class="kpi"><div class="label">Total Employees</div><div class="value" id="total">—</div><div class="sub">Unique employee records</div></div><div class="kpi"><div class="label">Employees Who Left</div><div class="value" id="left">—</div><div class="sub">Attrition = Yes</div></div><div class="kpi"><div class="label">Attrition Rate</div><div class="value" id="rate">—</div><div class="sub">Leavers / total employees</div></div><div class="kpi"><div class="label">Average Monthly Income</div><div class="value" id="income">—</div><div class="sub">Dataset income units</div></div></section>
<section class="charts"><article class="panel"><h2>Employees Who Left by Department</h2><p>Number of employees who left</p><div class="plot" id="dept"></div></article><article class="panel"><h2>Employees Who Left by Job Role</h2><p>Number of employees who left</p><div class="plot" id="job"></div></article><article class="panel"><h2>Attrition Rate by Age Group</h2><p>Leavers as a percentage of each age group</p><div class="plot" id="age"></div></article><article class="panel"><h2>Overtime and Attrition</h2><p>Attrition rate among overtime / non-overtime employees</p><div class="plot" id="overtimechart"></div></article><article class="panel"><h2>Attrition Rate by Income Group</h2><p>Leavers as a percentage of each income group</p><div class="plot" id="incomechart"></div></article><article class="panel"><h2>Attrition Rate by Job Satisfaction</h2><p>Comparison across satisfaction scores</p><div class="plot" id="satisfaction"></div></article></section>
<div class="foot">Source: IBM HR Analytics Employee Attrition & Performance (sample dataset). This is descriptive analysis, not proof of what causes employees to leave. Filters update all figures. This dashboard runs locally in your browser and does not upload employee records.</div></main><script>
const DATA=/*DATA_RECORDS*/;
const settings=[['department','Department'],['gender','Gender'],['overtime','OverTime'],['role','JobRole']];
settings.forEach(([id,key])=>{const s=document.getElementById(id);[...new Set(DATA.map(x=>x[key]))].sort().forEach(v=>{let o=document.createElement('option');o.value=v;o.textContent=v;s.appendChild(o)});s.addEventListener('change',render)});
const colors={blue:'#2874d0',teal:'#19a68c'};
function agg(data,key,rate,order){const map=new Map();data.forEach(r=>{let k=String(r[key]);if(!map.has(k))map.set(k,{n:0,left:0});let v=map.get(k);v.n++;v.left+=Number(r.AttritionFlag)});let a=[...map].map(([name,v])=>({name,value:rate?(v.n?100*v.left/v.n:0):v.left,n:v.n,left:v.left}));if(order){a.sort((x,y)=>order.indexOf(x.name)-order.indexOf(y.name))}else{a.sort((x,y)=>y.value-x.value)}return a}
function chart(id,arr,rate){let reverse=[...arr].reverse();Plotly.react(id,[{type:'bar',orientation:'h',x:reverse.map(x=>x.value),y:reverse.map(x=>x.name),marker:{color:rate?colors.teal:colors.blue},text:reverse.map(x=>rate?x.value.toFixed(1)+'%':String(x.value)),textposition:'outside',cliponaxis:false,hovertemplate:'%{y}<br>%{x:.1f}'+(rate?'%':' employees')+'<extra></extra>'}],{margin:{l:145,r:50,t:12,b:42},xaxis:{title:rate?'Attrition rate (%)':'Employees who left',gridcolor:'#edf1f6',zeroline:false},yaxis:{automargin:true},font:{family:'Segoe UI, Arial',size:11,color:'#54647a'},paper_bgcolor:'#fff',plot_bgcolor:'#fff',showlegend:false},{responsive:true,displayModeBar:false})}
function render(){const selected=Object.fromEntries(settings.map(([id,key])=>[key,document.getElementById(id).value]));const data=DATA.filter(r=>Object.entries(selected).every(([key,val])=>!val||r[key]===val));const total=data.length,left=data.reduce((s,r)=>s+Number(r.AttritionFlag),0),avg=total?data.reduce((s,r)=>s+Number(r.MonthlyIncome),0)/total:0;document.getElementById('total').textContent=total.toLocaleString();document.getElementById('left').textContent=left.toLocaleString();document.getElementById('rate').textContent=total?(100*left/total).toFixed(1)+'%':'—';document.getElementById('income').textContent=total?Math.round(avg).toLocaleString():'—';chart('dept',agg(data,'Department',false),false);chart('job',agg(data,'JobRole',false),false);chart('age',agg(data,'AgeGroup',true,['25 or younger','26–35','36–45','46–55','56+']),true);chart('overtimechart',agg(data,'OverTime',true),true);chart('incomechart',agg(data,'IncomeGroup',true,['Up to 3,000','3,001–6,000','6,001–10,000','Over 10,000']),true);chart('satisfaction',agg(data,'JobSatisfaction',true,['1','2','3','4']),true)}render();
</script></body></html>'''

if __name__=='__main__':
    try: main()
    except Exception as e:
        print('ERROR:',e)
        raise
