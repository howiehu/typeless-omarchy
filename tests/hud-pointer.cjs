// Execute the production HUD state adapter, including renderer title updates.
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const {resolve} = require('node:path');
const root = resolve(__dirname, '..');
const source = execFileSync('python', ['-c',
  "import runpy; print(runpy.run_path('runtime/prepare.py')['HUD_STATE'])"], {cwd:root,encoding:'utf8'}).trim();
function fixture(env={TYPELESS_OMARCHY_ACTIVE:'1',WAYLAND_DISPLAY:'wayland-1'}) {
  let title='Status', updates=0;const events=new Map();
  const window={isDestroyed:()=>false,getTitle:()=>title,
    setTitle:t=>{title=t;updates++;},on:(n,fn)=>events.set(n,fn)};
  const state=new Function('process','og',source+'; return typelessOmarchyHudState;')(
    {env},rects=>rects.filter(r=>r.right-r.left>=1&&r.bottom-r.top>=1).map(r=>({x:r.left,y:r.top,width:r.right-r.left,height:r.bottom-r.top})));
  return {state,window,events,get title(){return title},get updates(){return updates}};
}
const rects=[{left:10,right:60,top:10,bottom:40}];
const f=fixture();f.state(f.window,[]);assert.equal(f.title,'Status (idle)');
f.state(f.window,[]);assert.equal(f.updates,1);
f.state(f.window,rects);assert.equal(f.title,'Status [10,10,50,30]');
f.state(f.window,[{left:0,right:0,top:0,bottom:0}]);assert.equal(f.title,'Status (idle)');
let prevented=false;f.window.setTitle('Status');
f.events.get('page-title-updated')({preventDefault:()=>prevented=true});
assert(prevented);assert.equal(f.title,'Status (idle)');assert.equal(f.events.size,1);
for(const env of [{},{TYPELESS_OMARCHY_ACTIVE:'1'},{TYPELESS_OMARCHY_ACTIVE:'0',WAYLAND_DISPLAY:'wayland-1'}]){
 const other=fixture(env);other.state(other.window,[]);assert.equal(other.title,'Status');assert.equal(other.events.size,0);
}
f.state(null,[]);f.state({isDestroyed:()=>true},[]);
console.log('PASS HUD idle/visible transitions, degenerate bounds, renderer title protection and launch scope');
