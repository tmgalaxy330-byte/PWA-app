import asyncio, json, os, sys
from playwright.async_api import async_playwright
BASE=os.environ.get('LOGITORE_URL','http://localhost:8765')
URL=BASE+'/index.html'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out'); os.makedirs(OUT,exist_ok=True)
CHROME=os.environ.get('CHROME_PATH')
def launch_args(): return dict(executable_path=CHROME,args=['--no-sandbox']) if CHROME else dict(args=['--no-sandbox'])
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(**launch_args())
        ctx=await b.new_context(**p.devices['Pixel 7']); pg=await ctx.new_page()
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        # seed old-format data (template 'tree') to test migration
        old={'schema':1,'thoughts':[{'id':'old1','title':'旧ロジックツリー','template':'tree','status':'draft','pinned':False,'created':1,'updated':1,'root':{'id':'r','text':'旧課題','children':[],'label':None,'ph':None,'collapsed':False},'memo':'','mece':{'a':False,'b':False,'c':False},'reviews':[]}],'meta':{'onboarded':True}}
        await ctx.add_init_script("if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');localStorage.setItem('logitore.v1',JSON.stringify("+json.dumps(old)+"))}")
        await pg.goto(URL); await pg.wait_for_timeout(700)
        print('migrated template:', await pg.evaluate("S.thoughts[0].template"), '| row meta:', await pg.text_content('.row .meta'))
        await pg.click('#h-fab'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/n1_templates.png')
        await pg.click('[data-info=why]'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/n2_usage.png')
        await pg.click('#u-smp'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/n3_sample.png')
        print('overlays stacked', await pg.evaluate("document.querySelectorAll('#layer .ov').length"))
        await pg.click('#s-copy'); await pg.wait_for_timeout(900)
        print('view', await pg.evaluate('Nav.view'), '| title', await pg.evaluate('T().title'), '| nodes', await pg.evaluate("document.querySelectorAll('#outline .nd').length"), '| overlays', await pg.evaluate("document.querySelectorAll('#layer .ov').length"))
        await pg.screenshot(path=OUT+'/n4_copied.png')
        await pg.click('#e-back'); await pg.wait_for_timeout(500)
        # diagnosis
        await pg.click('#h-fab'); await pg.wait_for_timeout(500); await pg.click('#t-diag'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=OUT+'/n5_diag.png')
        await pg.click('#dg [data-v=q2]'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT+'/n6_diag_q2.png')
        await pg.click('#dg [data-v=sky]'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT+'/n7_diag_res.png')
        await pg.click('#dg-re'); await pg.wait_for_timeout(200); await pg.click('#dg [data-v=pros]'); await pg.wait_for_timeout(200)
        await pg.click('#dg-make'); await pg.wait_for_timeout(900)
        print('diag created', await pg.evaluate('T().template'), '| nodes', await pg.evaluate("document.querySelectorAll('#outline .nd').length"))
        await pg.click('#o-add'); await pg.wait_for_timeout(300)
        print('after 選択肢を追加 nodes', await pg.evaluate("document.querySelectorAll('#outline .nd').length"), '| add label', await pg.text_content('#o-add'))
        await pg.screenshot(path=OUT+'/n8_pros.png')
        # every sample copies & each template creates without error
        for k in ['why','how','pyramid','sky','pros','blank']:
            await pg.evaluate(f"createFrom('{k}')"); await pg.wait_for_timeout(500)
            await pg.evaluate("go('home')"); await pg.wait_for_timeout(200)
        for k in ['why','how','pyramid','sky','pros']:
            await pg.evaluate(f"openSample('{k}')"); await pg.wait_for_timeout(400)
            await pg.click('#s-copy'); await pg.wait_for_timeout(700)
            md=await pg.evaluate("toMarkdown(T(),null)")
            if k=='pros': print(md)
            await pg.evaluate("go('home')"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=OUT+'/n9_home.png')
        print('thoughts', await pg.evaluate('S.thoughts.length'))
        print('errors', errs)
        if errs: sys.exit(1)
        await b.close()
asyncio.run(main())
