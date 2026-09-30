"""Positive controls: known repairs only in a disposable copy, never trial input."""
import json,pathlib,shutil,tempfile
from trials import execute
from run import ROOT,environment,JAVA
work=pathlib.Path(tempfile.mkdtemp(prefix='logging-positive-control-'))
shutil.copy2(ROOT/'pom.xml',work/'pom.xml');shutil.copytree(ROOT/'src',work/'src');shutil.copytree(ROOT/'investigation/src',work/'investigation/src')
p=work/'investigation/src/test/java/com/ai/token/experiment/Defects.java';s=p.read_text()
for before,after in [('price + quantity','price * quantity'),('"eighty"','"8080"'),('/orders?count=two','/orders?count=2'),('"same@example.test"','"user" + id + "@example.test"'),('base.resolve("/wrong")','base.resolve("/price")'),('Integer.parseInt("ten")','Integer.parseInt("10")'),('.*service ready.*','.*worker ready.*')]:s=s.replace(before,after)
s=s.replace('return org.springframework.web.client.RestClient.create().get().uri(base.resolve("/price")).retrieve().body(Integer.class);','return Integer.parseInt(org.springframework.web.client.RestClient.create().get().uri(base.resolve("/price")).retrieve().body(String.class));')
p.write_text(s)
env=environment();env['PATH']=JAVA+'/bin:'+env['PATH'];results=[]
dest=ROOT/'investigation/positive-controls-v2';dest.mkdir(exist_ok=True)
for case in ['01','02','03','04','05','06','07','08']:
 cmd=['mvn','-o','-B','-ntp',f'-Dmaven.repo.local={ROOT}/investigation/.m2','-Pinvestigation','-Dtest=FailureCasesTest',f'-Dexperiment.case={case}','test']
 code,seconds=execute(cmd,work,dest/f'{case}.stdout',dest/f'{case}.stderr',90,env);results.append({'case':case,'exit':code,'seconds':seconds,'command':cmd})
 print(case,code,flush=True)
(dest/'results.json').write_text(json.dumps(results,indent=2));shutil.rmtree(work)
assert all(r['exit']==0 for r in results)
