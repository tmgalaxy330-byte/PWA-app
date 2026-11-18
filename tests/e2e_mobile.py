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
        dev=p.devices['Pixel 7']
        ctx=await b.new_context(**dev,accept_downloads=True)
        pg=await ctx.new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        pg.on('console',lambda m:errs.append('CONSOLE '+m.type+' '+m.text) if m.type in('error','warning') else None)
        await pg.goto(URL); await pg.wait_for_timeout(800)
        print('mode', await pg.evaluate('Nav.mode'), 'hasCW', await pg.evaluate('Back.hasCW'))
        await pg.screenshot(path=OUT+'/01_onboard.png')
        for _ in range(3):
            await pg.click('#ob-next'); await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=OUT+'/02_home_empty.png')
        await pg.click('#h-fab'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/03_templates.png')
        await pg.click('[data-k=pyramid]'); await pg.wait_for_timeout(900)
        print('view', await pg.evaluate('Nav.view'))
        await pg.fill('#ed-title','転職すべきか?')
        txs=await pg.query_selector_all('#outline .tx')
        print('nodes', len(txs))
        await txs[0].click(); await pg.keyboard.type('今は転職すべきだ')
        txs=await pg.query_selector_all('#outline .tx')
        await txs[1].click(); await pg.keyboard.type('成長機会が少ない')
        await pg.keyboard.press('Enter'); await pg.keyboard.type('給与が相場より低い')
        await pg.wait_for_timeout(300)
        print('nodebar on', await pg.evaluate("document.querySelector('#nodebar').classList.contains('on')"))
        await pg.keyboard.press('Tab'); await pg.wait_for_timeout(200)
        await pg.keyboard.press('Shift+Tab'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=OUT+'/04_editor.png')
        # undo
        n1=await pg.evaluate("document.querySelectorAll('#outline .nd').length")
        await pg.click('#e-undo'); await pg.wait_for_timeout(200)
        await pg.click('#e-redo'); await pg.wait_for_timeout(200)
        n2=await pg.evaluate("document.querySelectorAll('#outline .nd').length")
        print('nodes before/after undo-redo', n1, n2)
        # tree view
        await pg.click('[data-vw=tree]'); await pg.wait_for_timeout(400)
        await pg.screenshot(path=OUT+'/05_tree.png')
        await pg.click('[data-vw=outline]'); await pg.wait_for_timeout(300)
        # panel
        await pg.click('#e-panel'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/06_panel.png')
        await pg.click('#p-auto'); await pg.wait_for_timeout(700)
        await pg.screenshot(path=OUT+'/07_mece.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        print('overlays after esc', await pg.evaluate("document.querySelectorAll('#layer .ov').length"))
        await pg.click('#p-ai'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/08_ai.png')
        md=await pg.text_content('#ai-md'); print('MD head:', md[:120].replace('\n',' / '))
        await pg.fill('#ai-res','根拠1の給与比較の出典が不明です。'); await pg.click('#ai-save'); await pg.wait_for_timeout(500)
        print('reviews', await pg.evaluate("T().reviews.length"))
        await pg.click('#p-close'); await pg.wait_for_timeout(400)
        # PNG export
        async with pg.expect_download() as dl:
            await pg.evaluate('exportPng()')
        d=await dl.value; await d.save_as(OUT+'/export.png'); print('png', d.suggested_filename)
        # back via Esc (close request) after activation
        await pg.click('#ed-title'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        print('after 1st esc view', await pg.evaluate('Nav.view'), 'armed', await pg.evaluate('Nav.armed'))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
        print('after 2nd esc view', await pg.evaluate('Nav.view'))
        await pg.screenshot(path=OUT+'/09_home_list.png')
        # long press menu
        row=await pg.query_selector('.row .sw-c'); bb=await row.bounding_box()
        await pg.mouse.move(bb['x']+150,bb['y']+20); await pg.mouse.down(); await pg.wait_for_timeout(700); await pg.mouse.up(); await pg.wait_for_timeout(400)
        print('menu items', await pg.evaluate("document.querySelectorAll('.mi').length"))
        await pg.screenshot(path=OUT+'/10_longpress.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        # swipe
        await pg.mouse.move(bb['x']+250,bb['y']+20); await pg.mouse.down(); 
        for i in range(10): await pg.mouse.move(bb['x']+250-i*18,bb['y']+22); await pg.wait_for_timeout(16)
        await pg.mouse.up(); await pg.wait_for_timeout(400)
        print('row open', await pg.evaluate("!!document.querySelector('.row.open')"))
        await pg.screenshot(path=OUT+'/11_swipe.png')
        await pg.click('.row.open [data-act=dup]'); await pg.wait_for_timeout(400)
        print('thoughts', await pg.evaluate('S.thoughts.length'))
        # drill
        await pg.click('#h-drill'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=OUT+'/12_drill.png')
        for i in range(5):
            await pg.click('.ch[data-i="0"]'); await pg.wait_for_timeout(300)
            if i==0: await pg.screenshot(path=OUT+'/13_drill_ans.png')
            await pg.click('#d-next'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT+'/14_drill_result.png')
        print('drill', await pg.evaluate('JSON.stringify({s:S.drill.streak,t:S.drill.total,c:S.drill.correct,last:S.drill.lastDone})'))
        await pg.click('#d-home'); await pg.wait_for_timeout(500)
        # settings
        await pg.click('#h-menu'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=OUT+'/15_drawer.png')
        await pg.click('.nav[data-k=settings]'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=OUT+'/16_settings.png',full_page=True)
        await pg.click('#s-theme [data-v=light]'); await pg.wait_for_timeout(800)
        await pg.screenshot(path=OUT+'/17_settings_light.png')
        async with pg.expect_download() as dl:
            await pg.click('#s-exp')
        d=await dl.value; await d.save_as(OUT+'/backup.json'); print('backup', d.suggested_filename)
        # import merge
        await pg.set_input_files('#file',OUT+'/backup.json'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=OUT+'/18_import.png')
        await pg.click('.dlg .btn.pri'); await pg.wait_for_timeout(600)
        print('after merge thoughts', await pg.evaluate('S.thoughts.length'), 'view', await pg.evaluate('Nav.view'))
        # manual
        await pg.evaluate("go('settings')"); await pg.wait_for_timeout(300)
        await pg.click('#s-man'); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=OUT+'/19_manual.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        # errors log test
        await pg.evaluate("setTimeout(()=>{throw new Error('テスト用エラー')},0)"); await pg.wait_for_timeout(400)
        print('errors', await pg.evaluate('S.errors.length'))
        # reload persistence
        await pg.evaluate("go('home')"); await pg.wait_for_timeout(300)
        await pg.reload(); await pg.wait_for_timeout(900)
        print('after reload thoughts', await pg.evaluate('S.thoughts.length'), 'theme', await pg.evaluate('document.documentElement.dataset.theme'), 'notice', await pg.evaluate("!!document.querySelector('#h-notice')"))
        await pg.screenshot(path=OUT+'/20_reload_home.png')
        bad=[e for e in errs if 'テスト用エラー' not in e]; print('ERRORS:', bad)
        if bad: sys.exit(1)
        await b.close()
asyncio.run(main())
