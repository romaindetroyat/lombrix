/** Build the offline single-file preview from current sources, never an old solo. */
import {readFile,writeFile} from 'node:fs/promises';
const read=p=>readFile(p,'utf8'),escape=s=>s.replace(/<\/script/gi,'<\\/script');
const cssSafe=await read('site/style.css')+'\n'+await read('site/comfort.css');
let html=(await read('site/index.html')).replace(/<link[^>]+>/g,'');
html=html.replace('</head>',()=>'<style>'+cssSafe+'</style></head>');

let js='';
for(const name of ['engine','interaction','render-cache','art','renderer','audio','comfort','app']){
 let code=await read(`site/${name}.js`);
 code=code.replace(/^import .+?;\s*/gm,'').replace(/\bexport (?=const|class|function)/g,'');
 js+=code+'\n';
}
js=js.replace("if('serviceWorker'in navigator&&window.isSecureContext)",'if(false)');
js+=`\nfunction soloOnly(){dialog('VERSION SOLO','<h2>Partie contre l’ordinateur.</h2><p>Pour jouer entre amis, ouvre l’adresse HTTPS du serveur LOMBRIX. Ce fichier autonome ne connecte pas les téléphones.</p>');}
$('create-duel').onclick=soloOnly;$('create-tournament').onclick=soloOnly;$('join-room').onclick=soloOnly;`;
const boot=await read('site/boot.js');
html=html.replace(/<script src="\/boot\.js[^"]*"><\/script>/,()=>'<script>'+escape(boot)+'</script>');
html=html.replace(/<script type="module" src="\/app\.js[^"]*"><\/script>/,()=>"<script>(function(){'use strict';\n"+escape(js)+"\n})();</script>");
await writeFile('solo.html',html);console.log('solo.html regenerated from site/');
