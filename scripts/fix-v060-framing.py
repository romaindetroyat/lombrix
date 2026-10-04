"""Idempotent source migration for the 0.6 review checkpoint."""
from pathlib import Path
p=Path('site/renderer.js')
s=p.read_text()
if 'this.snapCamera=true;' not in s:
    before='this.camera={x:this.world.w/2,y:this.world.h/2};this.manualCamera=null;'
    assert before in s
    s=s.replace(before,'this.camera={x:this.world.w/2,y:this.world.h/2};this.snapCamera=true;this.manualCamera=null;')
    before='const follow=this.overview?1:Math.min(1,dt*(s.projectiles.length?13:6));'
    assert before in s
    s=s.replace(before,'// A freshly generated level must start on its active worm, not drift from the map centre.\n  if(this.snapCamera){this.camera={x:gx,y:gy};this.snapCamera=false;}\n  '+before)
    p.write_text(s)
    print('Initial camera now snaps to the playable focus before the first frame.')
else:
    print('Initial focus fix already applied.')
