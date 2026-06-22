(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const i of document.querySelectorAll('link[rel="modulepreload"]'))r(i);new MutationObserver(i=>{for(const o of i)if(o.type==="childList")for(const a of o.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&r(a)}).observe(document,{childList:!0,subtree:!0});function n(i){const o={};return i.integrity&&(o.integrity=i.integrity),i.referrerPolicy&&(o.referrerPolicy=i.referrerPolicy),i.crossOrigin==="use-credentials"?o.credentials="include":i.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function r(i){if(i.ep)return;i.ep=!0;const o=n(i);fetch(i.href,o)}})();var $e=!1,Re=!1,R=[],De=-1;function er(e){tr(e)}function tr(e){R.includes(e)||R.push(e),rr()}function nr(e){let t=R.indexOf(e);t!==-1&&t>De&&R.splice(t,1)}function rr(){!Re&&!$e&&($e=!0,queueMicrotask(ir))}function ir(){$e=!1,Re=!0;for(let e=0;e<R.length;e++)R[e](),De=e;R.length=0,De=-1,Re=!1}var U,z,J,Dt,Fe=!0;function or(e){Fe=!1,e(),Fe=!0}function ar(e){U=e.reactive,J=e.release,z=t=>e.effect(t,{scheduler:n=>{Fe?er(n):n()}}),Dt=e.raw}function wt(e){z=e}function sr(e){let t=()=>{};return[r=>{let i=z(r);return e._x_effects||(e._x_effects=new Set,e._x_runEffects=()=>{e._x_effects.forEach(o=>o())}),e._x_effects.add(i),t=()=>{i!==void 0&&(e._x_effects.delete(i),J(i))},i},()=>{t()}]}function Ft(e,t){let n=!0,r,i=z(()=>{let o=e();JSON.stringify(o),n?r=o:queueMicrotask(()=>{t(o,r),r=o}),n=!1});return()=>J(i)}var Bt=[],Nt=[],zt=[];function lr(e){zt.push(e)}function Qe(e,t){typeof t=="function"?(e._x_cleanups||(e._x_cleanups=[]),e._x_cleanups.push(t)):(t=e,Nt.push(t))}function Ht(e){Bt.push(e)}function Vt(e,t,n){e._x_attributeCleanups||(e._x_attributeCleanups={}),e._x_attributeCleanups[t]||(e._x_attributeCleanups[t]=[]),e._x_attributeCleanups[t].push(n)}function Wt(e,t){e._x_attributeCleanups&&Object.entries(e._x_attributeCleanups).forEach(([n,r])=>{(t===void 0||t.includes(n))&&(r.forEach(i=>i()),delete e._x_attributeCleanups[n])})}function dr(e){var t,n;for((t=e._x_effects)==null||t.forEach(nr);(n=e._x_cleanups)!=null&&n.length;)e._x_cleanups.pop()()}var et=new MutationObserver(it),tt=!1;function nt(){et.observe(document,{subtree:!0,childList:!0,attributes:!0,attributeOldValue:!0}),tt=!0}function Kt(){cr(),et.disconnect(),tt=!1}var Q=[];function cr(){let e=et.takeRecords();Q.push(()=>e.length>0&&it(e));let t=Q.length;queueMicrotask(()=>{if(Q.length===t)for(;Q.length>0;)Q.shift()()})}function x(e){if(!tt)return e();Kt();let t=e();return nt(),t}var rt=!1,be=[];function ur(){rt=!0}function fr(){rt=!1,it(be),be=[]}function it(e){if(rt){be=be.concat(e);return}let t=[],n=new Set,r=new Map,i=new Map;for(let o=0;o<e.length;o++)if(!e[o].target._x_ignoreMutationObserver&&(e[o].type==="childList"&&(e[o].removedNodes.forEach(a=>{a.nodeType===1&&a._x_marker&&n.add(a)}),e[o].addedNodes.forEach(a=>{if(a.nodeType===1){if(n.has(a)){n.delete(a);return}a._x_marker||t.push(a)}})),e[o].type==="attributes")){let a=e[o].target,s=e[o].attributeName,l=e[o].oldValue,d=()=>{r.has(a)||r.set(a,[]),r.get(a).push({name:s,value:a.getAttribute(s)})},c=()=>{i.has(a)||i.set(a,[]),i.get(a).push(s)};a.hasAttribute(s)&&l===null?d():a.hasAttribute(s)?(c(),d()):c()}i.forEach((o,a)=>{Wt(a,o)}),r.forEach((o,a)=>{Bt.forEach(s=>s(a,o))});for(let o of n)t.some(a=>a.contains(o))||Nt.forEach(a=>a(o));for(let o of t)o.isConnected&&zt.forEach(a=>a(o));t=null,n=null,r=null,i=null}function qt(e){return se(K(e))}function ae(e,t,n){return e._x_dataStack=[t,...K(n||e)],()=>{e._x_dataStack=e._x_dataStack.filter(r=>r!==t)}}function K(e){return e._x_dataStack?e._x_dataStack:typeof ShadowRoot=="function"&&e instanceof ShadowRoot?K(e.host):e.parentNode?K(e.parentNode):[]}function se(e){return new Proxy({objects:e},pr)}var pr={ownKeys({objects:e}){return Array.from(new Set(e.flatMap(t=>Object.keys(t))))},has({objects:e},t){return t==Symbol.unscopables?!1:e.some(n=>Object.prototype.hasOwnProperty.call(n,t)||Reflect.has(n,t))},get({objects:e},t,n){return t=="toJSON"?gr:Reflect.get(e.find(r=>Reflect.has(r,t))||{},t,n)},set({objects:e},t,n,r){const i=e.find(a=>Object.prototype.hasOwnProperty.call(a,t))||e[e.length-1],o=Object.getOwnPropertyDescriptor(i,t);return o!=null&&o.set&&(o!=null&&o.get)?o.set.call(r,n)||!0:Reflect.set(i,t,n)}};function gr(){return Reflect.ownKeys(this).reduce((t,n)=>(t[n]=Reflect.get(this,n),t),{})}function Ut(e){let t=r=>typeof r=="object"&&!Array.isArray(r)&&r!==null,n=(r,i="")=>{Object.entries(Object.getOwnPropertyDescriptors(r)).forEach(([o,{value:a,enumerable:s}])=>{if(s===!1||a===void 0||typeof a=="object"&&a!==null&&a.__v_skip)return;let l=i===""?o:`${i}.${o}`;typeof a=="object"&&a!==null&&a._x_interceptor?r[o]=a.initialize(e,l,o):t(a)&&a!==r&&!(a instanceof Element)&&n(a,l)})};return n(e)}function Jt(e,t=()=>{}){let n={initialValue:void 0,_x_interceptor:!0,initialize(r,i,o){return e(this.initialValue,()=>hr(r,i),a=>Be(r,i,a),i,o)}};return t(n),r=>{if(typeof r=="object"&&r!==null&&r._x_interceptor){let i=n.initialize.bind(n);n.initialize=(o,a,s)=>{let l=r.initialize(o,a,s);return n.initialValue=l,i(o,a,s)}}else n.initialValue=r;return n}}function hr(e,t){return t.split(".").reduce((n,r)=>n[r],e)}function Be(e,t,n){if(typeof t=="string"&&(t=t.split(".")),t.length===1)e[t[0]]=n;else{if(t.length===0)throw error;return e[t[0]]||(e[t[0]]={}),Be(e[t[0]],t.slice(1),n)}}var Gt={};function S(e,t){Gt[e]=t}function Ne(e,t){let n=xr(t);return Object.entries(Gt).forEach(([r,i])=>{Object.defineProperty(e,`$${r}`,{get(){return i(t,n)},enumerable:!1})}),e}function xr(e){let[t,n]=tn(e),r={interceptor:Jt,...t};return Qe(e,n),r}function mr(e,t,n,...r){try{return n(...r)}catch(i){oe(i,e,t)}}function oe(e,t,n=void 0){e=Object.assign(e??{message:"No error message given."},{el:t,expression:n}),console.warn(`Alpine Expression Error: ${e.message}

${n?'Expression: "'+n+`"

`:""}`,t),setTimeout(()=>{throw e},0)}var xe=!0;function Yt(e){let t=xe;xe=!1;let n=e();return xe=t,n}function D(e,t,n={}){let r;return w(e,t)(i=>r=i,n),r}function w(...e){return Xt(...e)}var Xt=Zt;function br(e){Xt=e}function Zt(e,t){let n={};Ne(n,e);let r=[n,...K(e)],i=typeof t=="function"?vr(r,t):wr(r,t,e);return mr.bind(null,e,t,i)}function vr(e,t){return(n=()=>{},{scope:r={},params:i=[]}={})=>{let o=t.apply(se([r,...e]),i);ve(n,o)}}var Le={};function yr(e,t){if(Le[e])return Le[e];let n=Object.getPrototypeOf(async function(){}).constructor,r=/^[\n\s]*if.*\(.*\)/.test(e.trim())||/^(let|const)\s/.test(e.trim())?`(async()=>{ ${e} })()`:e,o=(()=>{try{let a=new n(["__self","scope"],`with (scope) { __self.result = ${r} }; __self.finished = true; return __self.result;`);return Object.defineProperty(a,"name",{value:`[Alpine] ${e}`}),a}catch(a){return oe(a,t,e),Promise.resolve()}})();return Le[e]=o,o}function wr(e,t,n){let r=yr(t,n);return(i=()=>{},{scope:o={},params:a=[]}={})=>{r.result=void 0,r.finished=!1;let s=se([o,...e]);if(typeof r=="function"){let l=r(r,s).catch(d=>oe(d,n,t));r.finished?(ve(i,r.result,s,a,n),r.result=void 0):l.then(d=>{ve(i,d,s,a,n)}).catch(d=>oe(d,n,t)).finally(()=>r.result=void 0)}}}function ve(e,t,n,r,i){if(xe&&typeof t=="function"){let o=t.apply(n,r);o instanceof Promise?o.then(a=>ve(e,a,n,r)).catch(a=>oe(a,i,t)):e(o)}else typeof t=="object"&&t instanceof Promise?t.then(o=>e(o)):e(t)}var ot="x-";function G(e=""){return ot+e}function _r(e){ot=e}var ye={};function b(e,t){return ye[e]=t,{before(n){if(!ye[n]){console.warn(String.raw`Cannot find directive \`${n}\`. \`${e}\` will use the default order of execution`);return}const r=$.indexOf(n);$.splice(r>=0?r:$.indexOf("DEFAULT"),0,e)}}}function kr(e){return Object.keys(ye).includes(e)}function at(e,t,n){if(t=Array.from(t),e._x_virtualDirectives){let o=Object.entries(e._x_virtualDirectives).map(([s,l])=>({name:s,value:l})),a=Qt(o);o=o.map(s=>a.find(l=>l.name===s.name)?{name:`x-bind:${s.name}`,value:`"${s.value}"`}:s),t=t.concat(o)}let r={};return t.map(on((o,a)=>r[o]=a)).filter(sn).map(Ar(r,n)).sort(Er).map(o=>Sr(e,o))}function Qt(e){return Array.from(e).map(on()).filter(t=>!sn(t))}var ze=!1,ne=new Map,en=Symbol();function Cr(e){ze=!0;let t=Symbol();en=t,ne.set(t,[]);let n=()=>{for(;ne.get(t).length;)ne.get(t).shift()();ne.delete(t)},r=()=>{ze=!1,n()};e(n),r()}function tn(e){let t=[],n=s=>t.push(s),[r,i]=sr(e);return t.push(i),[{Alpine:le,effect:r,cleanup:n,evaluateLater:w.bind(w,e),evaluate:D.bind(D,e)},()=>t.forEach(s=>s())]}function Sr(e,t){let n=()=>{},r=ye[t.type]||n,[i,o]=tn(e);Vt(e,t.original,o);let a=()=>{e._x_ignore||e._x_ignoreSelf||(r.inline&&r.inline(e,t,i),r=r.bind(r,e,t,i),ze?ne.get(en).push(r):r())};return a.runCleanups=o,a}var nn=(e,t)=>({name:n,value:r})=>(n.startsWith(e)&&(n=n.replace(e,t)),{name:n,value:r}),rn=e=>e;function on(e=()=>{}){return({name:t,value:n})=>{let{name:r,value:i}=an.reduce((o,a)=>a(o),{name:t,value:n});return r!==t&&e(r,t),{name:r,value:i}}}var an=[];function st(e){an.push(e)}function sn({name:e}){return ln().test(e)}var ln=()=>new RegExp(`^${ot}([^:^.]+)\\b`);function Ar(e,t){return({name:n,value:r})=>{let i=n.match(ln()),o=n.match(/:([a-zA-Z0-9\-_:]+)/),a=n.match(/\.[^.\]]+(?=[^\]]*$)/g)||[],s=t||e[n]||n;return{type:i?i[1]:null,value:o?o[1]:null,modifiers:a.map(l=>l.replace(".","")),expression:r,original:s}}}var He="DEFAULT",$=["ignore","ref","data","id","anchor","bind","init","for","model","modelable","transition","show","if",He,"teleport"];function Er(e,t){let n=$.indexOf(e.type)===-1?He:e.type,r=$.indexOf(t.type)===-1?He:t.type;return $.indexOf(n)-$.indexOf(r)}function re(e,t,n={}){e.dispatchEvent(new CustomEvent(t,{detail:n,bubbles:!0,composed:!0,cancelable:!0}))}function N(e,t){if(typeof ShadowRoot=="function"&&e instanceof ShadowRoot){Array.from(e.children).forEach(i=>N(i,t));return}let n=!1;if(t(e,()=>n=!0),n)return;let r=e.firstElementChild;for(;r;)N(r,t),r=r.nextElementSibling}function k(e,...t){console.warn(`Alpine Warning: ${e}`,...t)}var _t=!1;function Pr(){_t&&k("Alpine has already been initialized on this page. Calling Alpine.start() more than once can cause problems."),_t=!0,document.body||k("Unable to initialize. Trying to load Alpine before `<body>` is available. Did you forget to add `defer` in Alpine's `<script>` tag?"),re(document,"alpine:init"),re(document,"alpine:initializing"),nt(),lr(t=>E(t,N)),Qe(t=>X(t)),Ht((t,n)=>{at(t,n).forEach(r=>r())});let e=t=>!ke(t.parentElement,!0);Array.from(document.querySelectorAll(un().join(","))).filter(e).forEach(t=>{E(t)}),re(document,"alpine:initialized"),setTimeout(()=>{Ir()})}var lt=[],dn=[];function cn(){return lt.map(e=>e())}function un(){return lt.concat(dn).map(e=>e())}function fn(e){lt.push(e)}function pn(e){dn.push(e)}function ke(e,t=!1){return Y(e,n=>{if((t?un():cn()).some(i=>n.matches(i)))return!0})}function Y(e,t){if(e){if(t(e))return e;if(e._x_teleportBack&&(e=e._x_teleportBack),!!e.parentElement)return Y(e.parentElement,t)}}function Mr(e){return cn().some(t=>e.matches(t))}var gn=[];function Lr(e){gn.push(e)}var Or=1;function E(e,t=N,n=()=>{}){Y(e,r=>r._x_ignore)||Cr(()=>{t(e,(r,i)=>{r._x_marker||(n(r,i),gn.forEach(o=>o(r,i)),at(r,r.attributes).forEach(o=>o()),r._x_ignore||(r._x_marker=Or++),r._x_ignore&&i())})})}function X(e,t=N){t(e,n=>{dr(n),Wt(n),delete n._x_marker})}function Ir(){[["ui","dialog",["[x-dialog], [x-popover]"]],["anchor","anchor",["[x-anchor]"]],["sort","sort",["[x-sort]"]]].forEach(([t,n,r])=>{kr(n)||r.some(i=>{if(document.querySelector(i))return k(`found "${i}", but missing ${t} plugin`),!0})})}var Ve=[],dt=!1;function ct(e=()=>{}){return queueMicrotask(()=>{dt||setTimeout(()=>{We()})}),new Promise(t=>{Ve.push(()=>{e(),t()})})}function We(){for(dt=!1;Ve.length;)Ve.shift()()}function jr(){dt=!0}function ut(e,t){return Array.isArray(t)?kt(e,t.join(" ")):typeof t=="object"&&t!==null?Tr(e,t):typeof t=="function"?ut(e,t()):kt(e,t)}function kt(e,t){let n=i=>i.split(" ").filter(o=>!e.classList.contains(o)).filter(Boolean),r=i=>(e.classList.add(...i),()=>{e.classList.remove(...i)});return t=t===!0?t="":t||"",r(n(t))}function Tr(e,t){let n=s=>s.split(" ").filter(Boolean),r=Object.entries(t).flatMap(([s,l])=>l?n(s):!1).filter(Boolean),i=Object.entries(t).flatMap(([s,l])=>l?!1:n(s)).filter(Boolean),o=[],a=[];return i.forEach(s=>{e.classList.contains(s)&&(e.classList.remove(s),a.push(s))}),r.forEach(s=>{e.classList.contains(s)||(e.classList.add(s),o.push(s))}),()=>{a.forEach(s=>e.classList.add(s)),o.forEach(s=>e.classList.remove(s))}}function Ce(e,t){return typeof t=="object"&&t!==null?$r(e,t):Rr(e,t)}function $r(e,t){let n={};return Object.entries(t).forEach(([r,i])=>{n[r]=e.style[r],r.startsWith("--")||(r=Dr(r)),e.style.setProperty(r,i)}),setTimeout(()=>{e.style.length===0&&e.removeAttribute("style")}),()=>{Ce(e,n)}}function Rr(e,t){let n=e.getAttribute("style",t);return e.setAttribute("style",t),()=>{e.setAttribute("style",n||"")}}function Dr(e){return e.replace(/([a-z])([A-Z])/g,"$1-$2").toLowerCase()}function Ke(e,t=()=>{}){let n=!1;return function(){n?t.apply(this,arguments):(n=!0,e.apply(this,arguments))}}b("transition",(e,{value:t,modifiers:n,expression:r},{evaluate:i})=>{typeof r=="function"&&(r=i(r)),r!==!1&&(!r||typeof r=="boolean"?Br(e,n,t):Fr(e,r,t))});function Fr(e,t,n){hn(e,ut,""),{enter:i=>{e._x_transition.enter.during=i},"enter-start":i=>{e._x_transition.enter.start=i},"enter-end":i=>{e._x_transition.enter.end=i},leave:i=>{e._x_transition.leave.during=i},"leave-start":i=>{e._x_transition.leave.start=i},"leave-end":i=>{e._x_transition.leave.end=i}}[n](t)}function Br(e,t,n){hn(e,Ce);let r=!t.includes("in")&&!t.includes("out")&&!n,i=r||t.includes("in")||["enter"].includes(n),o=r||t.includes("out")||["leave"].includes(n);t.includes("in")&&!r&&(t=t.filter((h,m)=>m<t.indexOf("out"))),t.includes("out")&&!r&&(t=t.filter((h,m)=>m>t.indexOf("out")));let a=!t.includes("opacity")&&!t.includes("scale"),s=a||t.includes("opacity"),l=a||t.includes("scale"),d=s?0:1,c=l?ee(t,"scale",95)/100:1,f=ee(t,"delay",0)/1e3,p=ee(t,"origin","center"),v="opacity, transform",P=ee(t,"duration",150)/1e3,de=ee(t,"duration",75)/1e3,u="cubic-bezier(0.4, 0.0, 0.2, 1)";i&&(e._x_transition.enter.during={transformOrigin:p,transitionDelay:`${f}s`,transitionProperty:v,transitionDuration:`${P}s`,transitionTimingFunction:u},e._x_transition.enter.start={opacity:d,transform:`scale(${c})`},e._x_transition.enter.end={opacity:1,transform:"scale(1)"}),o&&(e._x_transition.leave.during={transformOrigin:p,transitionDelay:`${f}s`,transitionProperty:v,transitionDuration:`${de}s`,transitionTimingFunction:u},e._x_transition.leave.start={opacity:1,transform:"scale(1)"},e._x_transition.leave.end={opacity:d,transform:`scale(${c})`})}function hn(e,t,n={}){e._x_transition||(e._x_transition={enter:{during:n,start:n,end:n},leave:{during:n,start:n,end:n},in(r=()=>{},i=()=>{}){qe(e,t,{during:this.enter.during,start:this.enter.start,end:this.enter.end},r,i)},out(r=()=>{},i=()=>{}){qe(e,t,{during:this.leave.during,start:this.leave.start,end:this.leave.end},r,i)}})}window.Element.prototype._x_toggleAndCascadeWithTransitions=function(e,t,n,r){const i=document.visibilityState==="visible"?requestAnimationFrame:setTimeout;let o=()=>i(n);if(t){e._x_transition&&(e._x_transition.enter||e._x_transition.leave)?e._x_transition.enter&&(Object.entries(e._x_transition.enter.during).length||Object.entries(e._x_transition.enter.start).length||Object.entries(e._x_transition.enter.end).length)?e._x_transition.in(n):o():e._x_transition?e._x_transition.in(n):o();return}e._x_hidePromise=e._x_transition?new Promise((a,s)=>{e._x_transition.out(()=>{},()=>a(r)),e._x_transitioning&&e._x_transitioning.beforeCancel(()=>s({isFromCancelledTransition:!0}))}):Promise.resolve(r),queueMicrotask(()=>{let a=xn(e);a?(a._x_hideChildren||(a._x_hideChildren=[]),a._x_hideChildren.push(e)):i(()=>{let s=l=>{let d=Promise.all([l._x_hidePromise,...(l._x_hideChildren||[]).map(s)]).then(([c])=>c==null?void 0:c());return delete l._x_hidePromise,delete l._x_hideChildren,d};s(e).catch(l=>{if(!l.isFromCancelledTransition)throw l})})})};function xn(e){let t=e.parentNode;if(t)return t._x_hidePromise?t:xn(t)}function qe(e,t,{during:n,start:r,end:i}={},o=()=>{},a=()=>{}){if(e._x_transitioning&&e._x_transitioning.cancel(),Object.keys(n).length===0&&Object.keys(r).length===0&&Object.keys(i).length===0){o(),a();return}let s,l,d;Nr(e,{start(){s=t(e,r)},during(){l=t(e,n)},before:o,end(){s(),d=t(e,i)},after:a,cleanup(){l(),d()}})}function Nr(e,t){let n,r,i,o=Ke(()=>{x(()=>{n=!0,r||t.before(),i||(t.end(),We()),t.after(),e.isConnected&&t.cleanup(),delete e._x_transitioning})});e._x_transitioning={beforeCancels:[],beforeCancel(a){this.beforeCancels.push(a)},cancel:Ke(function(){for(;this.beforeCancels.length;)this.beforeCancels.shift()();o()}),finish:o},x(()=>{t.start(),t.during()}),jr(),requestAnimationFrame(()=>{if(n)return;let a=Number(getComputedStyle(e).transitionDuration.replace(/,.*/,"").replace("s",""))*1e3,s=Number(getComputedStyle(e).transitionDelay.replace(/,.*/,"").replace("s",""))*1e3;a===0&&(a=Number(getComputedStyle(e).animationDuration.replace("s",""))*1e3),x(()=>{t.before()}),r=!0,requestAnimationFrame(()=>{n||(x(()=>{t.end()}),We(),setTimeout(e._x_transitioning.finish,a+s),i=!0)})})}function ee(e,t,n){if(e.indexOf(t)===-1)return n;const r=e[e.indexOf(t)+1];if(!r||t==="scale"&&isNaN(r))return n;if(t==="duration"||t==="delay"){let i=r.match(/([0-9]+)ms/);if(i)return i[1]}return t==="origin"&&["top","right","left","center","bottom"].includes(e[e.indexOf(t)+2])?[r,e[e.indexOf(t)+2]].join(" "):r}var O=!1;function j(e,t=()=>{}){return(...n)=>O?t(...n):e(...n)}function zr(e){return(...t)=>O&&e(...t)}var mn=[];function Se(e){mn.push(e)}function Hr(e,t){mn.forEach(n=>n(e,t)),O=!0,bn(()=>{E(t,(n,r)=>{r(n,()=>{})})}),O=!1}var Ue=!1;function Vr(e,t){t._x_dataStack||(t._x_dataStack=e._x_dataStack),O=!0,Ue=!0,bn(()=>{Wr(t)}),O=!1,Ue=!1}function Wr(e){let t=!1;E(e,(r,i)=>{N(r,(o,a)=>{if(t&&Mr(o))return a();t=!0,i(o,a)})})}function bn(e){let t=z;wt((n,r)=>{let i=t(n);return J(i),()=>{}}),e(),wt(t)}function vn(e,t,n,r=[]){switch(e._x_bindings||(e._x_bindings=U({})),e._x_bindings[t]=n,t=r.includes("camel")?Zr(t):t,t){case"value":Kr(e,n);break;case"style":Ur(e,n);break;case"class":qr(e,n);break;case"selected":case"checked":Jr(e,t,n);break;default:yn(e,t,n);break}}function Kr(e,t){if(kn(e))e.attributes.value===void 0&&(e.value=t),window.fromModel&&(typeof t=="boolean"?e.checked=me(e.value)===t:e.checked=Ct(e.value,t));else if(ft(e))Number.isInteger(t)?e.value=t:!Array.isArray(t)&&typeof t!="boolean"&&![null,void 0].includes(t)?e.value=String(t):Array.isArray(t)?e.checked=t.some(n=>Ct(n,e.value)):e.checked=!!t;else if(e.tagName==="SELECT")Xr(e,t);else{if(e.value===t)return;e.value=t===void 0?"":t}}function qr(e,t){e._x_undoAddedClasses&&e._x_undoAddedClasses(),e._x_undoAddedClasses=ut(e,t)}function Ur(e,t){e._x_undoAddedStyles&&e._x_undoAddedStyles(),e._x_undoAddedStyles=Ce(e,t)}function Jr(e,t,n){yn(e,t,n),Yr(e,t,n)}function yn(e,t,n){[null,void 0,!1].includes(n)&&ei(t)?e.removeAttribute(t):(wn(t)&&(n=t),Gr(e,t,n))}function Gr(e,t,n){e.getAttribute(t)!=n&&e.setAttribute(t,n)}function Yr(e,t,n){e[t]!==n&&(e[t]=n)}function Xr(e,t){const n=[].concat(t).map(r=>r+"");Array.from(e.options).forEach(r=>{r.selected=n.includes(r.value)})}function Zr(e){return e.toLowerCase().replace(/-(\w)/g,(t,n)=>n.toUpperCase())}function Ct(e,t){return e==t}function me(e){return[1,"1","true","on","yes",!0].includes(e)?!0:[0,"0","false","off","no",!1].includes(e)?!1:e?!!e:null}var Qr=new Set(["allowfullscreen","async","autofocus","autoplay","checked","controls","default","defer","disabled","formnovalidate","inert","ismap","itemscope","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","selected","shadowrootclonable","shadowrootdelegatesfocus","shadowrootserializable"]);function wn(e){return Qr.has(e)}function ei(e){return!["aria-pressed","aria-checked","aria-expanded","aria-selected"].includes(e)}function ti(e,t,n){return e._x_bindings&&e._x_bindings[t]!==void 0?e._x_bindings[t]:_n(e,t,n)}function ni(e,t,n,r=!0){if(e._x_bindings&&e._x_bindings[t]!==void 0)return e._x_bindings[t];if(e._x_inlineBindings&&e._x_inlineBindings[t]!==void 0){let i=e._x_inlineBindings[t];return i.extract=r,Yt(()=>D(e,i.expression))}return _n(e,t,n)}function _n(e,t,n){let r=e.getAttribute(t);return r===null?typeof n=="function"?n():n:r===""?!0:wn(t)?!![t,"true"].includes(r):r}function ft(e){return e.type==="checkbox"||e.localName==="ui-checkbox"||e.localName==="ui-switch"}function kn(e){return e.type==="radio"||e.localName==="ui-radio"}function Cn(e,t){var n;return function(){var r=this,i=arguments,o=function(){n=null,e.apply(r,i)};clearTimeout(n),n=setTimeout(o,t)}}function Sn(e,t){let n;return function(){let r=this,i=arguments;n||(e.apply(r,i),n=!0,setTimeout(()=>n=!1,t))}}function An({get:e,set:t},{get:n,set:r}){let i=!0,o,a=z(()=>{let s=e(),l=n();if(i)r(Oe(s)),i=!1;else{let d=JSON.stringify(s),c=JSON.stringify(l);d!==o?r(Oe(s)):d!==c&&t(Oe(l))}o=JSON.stringify(e()),JSON.stringify(n())});return()=>{J(a)}}function Oe(e){return typeof e=="object"?JSON.parse(JSON.stringify(e)):e}function ri(e){(Array.isArray(e)?e:[e]).forEach(n=>n(le))}var T={},St=!1;function ii(e,t){if(St||(T=U(T),St=!0),t===void 0)return T[e];T[e]=t,Ut(T[e]),typeof t=="object"&&t!==null&&t.hasOwnProperty("init")&&typeof t.init=="function"&&T[e].init()}function oi(){return T}var En={};function ai(e,t){let n=typeof t!="function"?()=>t:t;return e instanceof Element?Pn(e,n()):(En[e]=n,()=>{})}function si(e){return Object.entries(En).forEach(([t,n])=>{Object.defineProperty(e,t,{get(){return(...r)=>n(...r)}})}),e}function Pn(e,t,n){let r=[];for(;r.length;)r.pop()();let i=Object.entries(t).map(([a,s])=>({name:a,value:s})),o=Qt(i);return i=i.map(a=>o.find(s=>s.name===a.name)?{name:`x-bind:${a.name}`,value:`"${a.value}"`}:a),at(e,i,n).map(a=>{r.push(a.runCleanups),a()}),()=>{for(;r.length;)r.pop()()}}var Mn={};function li(e,t){Mn[e]=t}function di(e,t){return Object.entries(Mn).forEach(([n,r])=>{Object.defineProperty(e,n,{get(){return(...i)=>r.bind(t)(...i)},enumerable:!1})}),e}var ci={get reactive(){return U},get release(){return J},get effect(){return z},get raw(){return Dt},version:"3.14.9",flushAndStopDeferringMutations:fr,dontAutoEvaluateFunctions:Yt,disableEffectScheduling:or,startObservingMutations:nt,stopObservingMutations:Kt,setReactivityEngine:ar,onAttributeRemoved:Vt,onAttributesAdded:Ht,closestDataStack:K,skipDuringClone:j,onlyDuringClone:zr,addRootSelector:fn,addInitSelector:pn,interceptClone:Se,addScopeToNode:ae,deferMutations:ur,mapAttributes:st,evaluateLater:w,interceptInit:Lr,setEvaluator:br,mergeProxies:se,extractProp:ni,findClosest:Y,onElRemoved:Qe,closestRoot:ke,destroyTree:X,interceptor:Jt,transition:qe,setStyles:Ce,mutateDom:x,directive:b,entangle:An,throttle:Sn,debounce:Cn,evaluate:D,initTree:E,nextTick:ct,prefixed:G,prefix:_r,plugin:ri,magic:S,store:ii,start:Pr,clone:Vr,cloneNode:Hr,bound:ti,$data:qt,watch:Ft,walk:N,data:li,bind:ai},le=ci;function ui(e,t){const n=Object.create(null),r=e.split(",");for(let i=0;i<r.length;i++)n[r[i]]=!0;return i=>!!n[i]}var fi=Object.freeze({}),pi=Object.prototype.hasOwnProperty,Ae=(e,t)=>pi.call(e,t),F=Array.isArray,ie=e=>Ln(e)==="[object Map]",gi=e=>typeof e=="string",pt=e=>typeof e=="symbol",Ee=e=>e!==null&&typeof e=="object",hi=Object.prototype.toString,Ln=e=>hi.call(e),On=e=>Ln(e).slice(8,-1),gt=e=>gi(e)&&e!=="NaN"&&e[0]!=="-"&&""+parseInt(e,10)===e,xi=e=>{const t=Object.create(null);return n=>t[n]||(t[n]=e(n))},mi=xi(e=>e.charAt(0).toUpperCase()+e.slice(1)),In=(e,t)=>e!==t&&(e===e||t===t),Je=new WeakMap,te=[],A,B=Symbol("iterate"),Ge=Symbol("Map key iterate");function bi(e){return e&&e._isEffect===!0}function vi(e,t=fi){bi(e)&&(e=e.raw);const n=_i(e,t);return t.lazy||n(),n}function yi(e){e.active&&(jn(e),e.options.onStop&&e.options.onStop(),e.active=!1)}var wi=0;function _i(e,t){const n=function(){if(!n.active)return e();if(!te.includes(n)){jn(n);try{return Ci(),te.push(n),A=n,e()}finally{te.pop(),Tn(),A=te[te.length-1]}}};return n.id=wi++,n.allowRecurse=!!t.allowRecurse,n._isEffect=!0,n.active=!0,n.raw=e,n.deps=[],n.options=t,n}function jn(e){const{deps:t}=e;if(t.length){for(let n=0;n<t.length;n++)t[n].delete(e);t.length=0}}var q=!0,ht=[];function ki(){ht.push(q),q=!1}function Ci(){ht.push(q),q=!0}function Tn(){const e=ht.pop();q=e===void 0?!0:e}function C(e,t,n){if(!q||A===void 0)return;let r=Je.get(e);r||Je.set(e,r=new Map);let i=r.get(n);i||r.set(n,i=new Set),i.has(A)||(i.add(A),A.deps.push(i),A.options.onTrack&&A.options.onTrack({effect:A,target:e,type:t,key:n}))}function I(e,t,n,r,i,o){const a=Je.get(e);if(!a)return;const s=new Set,l=c=>{c&&c.forEach(f=>{(f!==A||f.allowRecurse)&&s.add(f)})};if(t==="clear")a.forEach(l);else if(n==="length"&&F(e))a.forEach((c,f)=>{(f==="length"||f>=r)&&l(c)});else switch(n!==void 0&&l(a.get(n)),t){case"add":F(e)?gt(n)&&l(a.get("length")):(l(a.get(B)),ie(e)&&l(a.get(Ge)));break;case"delete":F(e)||(l(a.get(B)),ie(e)&&l(a.get(Ge)));break;case"set":ie(e)&&l(a.get(B));break}const d=c=>{c.options.onTrigger&&c.options.onTrigger({effect:c,target:e,key:n,type:t,newValue:r,oldValue:i,oldTarget:o}),c.options.scheduler?c.options.scheduler(c):c()};s.forEach(d)}var Si=ui("__proto__,__v_isRef,__isVue"),$n=new Set(Object.getOwnPropertyNames(Symbol).map(e=>Symbol[e]).filter(pt)),Ai=Rn(),Ei=Rn(!0),At=Pi();function Pi(){const e={};return["includes","indexOf","lastIndexOf"].forEach(t=>{e[t]=function(...n){const r=g(this);for(let o=0,a=this.length;o<a;o++)C(r,"get",o+"");const i=r[t](...n);return i===-1||i===!1?r[t](...n.map(g)):i}}),["push","pop","shift","unshift","splice"].forEach(t=>{e[t]=function(...n){ki();const r=g(this)[t].apply(this,n);return Tn(),r}}),e}function Rn(e=!1,t=!1){return function(r,i,o){if(i==="__v_isReactive")return!e;if(i==="__v_isReadonly")return e;if(i==="__v_raw"&&o===(e?t?Hi:Nn:t?zi:Bn).get(r))return r;const a=F(r);if(!e&&a&&Ae(At,i))return Reflect.get(At,i,o);const s=Reflect.get(r,i,o);return(pt(i)?$n.has(i):Si(i))||(e||C(r,"get",i),t)?s:Ye(s)?!a||!gt(i)?s.value:s:Ee(s)?e?zn(s):vt(s):s}}var Mi=Li();function Li(e=!1){return function(n,r,i,o){let a=n[r];if(!e&&(i=g(i),a=g(a),!F(n)&&Ye(a)&&!Ye(i)))return a.value=i,!0;const s=F(n)&&gt(r)?Number(r)<n.length:Ae(n,r),l=Reflect.set(n,r,i,o);return n===g(o)&&(s?In(i,a)&&I(n,"set",r,i,a):I(n,"add",r,i)),l}}function Oi(e,t){const n=Ae(e,t),r=e[t],i=Reflect.deleteProperty(e,t);return i&&n&&I(e,"delete",t,void 0,r),i}function Ii(e,t){const n=Reflect.has(e,t);return(!pt(t)||!$n.has(t))&&C(e,"has",t),n}function ji(e){return C(e,"iterate",F(e)?"length":B),Reflect.ownKeys(e)}var Ti={get:Ai,set:Mi,deleteProperty:Oi,has:Ii,ownKeys:ji},$i={get:Ei,set(e,t){return console.warn(`Set operation on key "${String(t)}" failed: target is readonly.`,e),!0},deleteProperty(e,t){return console.warn(`Delete operation on key "${String(t)}" failed: target is readonly.`,e),!0}},xt=e=>Ee(e)?vt(e):e,mt=e=>Ee(e)?zn(e):e,bt=e=>e,Pe=e=>Reflect.getPrototypeOf(e);function ce(e,t,n=!1,r=!1){e=e.__v_raw;const i=g(e),o=g(t);t!==o&&!n&&C(i,"get",t),!n&&C(i,"get",o);const{has:a}=Pe(i),s=r?bt:n?mt:xt;if(a.call(i,t))return s(e.get(t));if(a.call(i,o))return s(e.get(o));e!==i&&e.get(t)}function ue(e,t=!1){const n=this.__v_raw,r=g(n),i=g(e);return e!==i&&!t&&C(r,"has",e),!t&&C(r,"has",i),e===i?n.has(e):n.has(e)||n.has(i)}function fe(e,t=!1){return e=e.__v_raw,!t&&C(g(e),"iterate",B),Reflect.get(e,"size",e)}function Et(e){e=g(e);const t=g(this);return Pe(t).has.call(t,e)||(t.add(e),I(t,"add",e,e)),this}function Pt(e,t){t=g(t);const n=g(this),{has:r,get:i}=Pe(n);let o=r.call(n,e);o?Fn(n,r,e):(e=g(e),o=r.call(n,e));const a=i.call(n,e);return n.set(e,t),o?In(t,a)&&I(n,"set",e,t,a):I(n,"add",e,t),this}function Mt(e){const t=g(this),{has:n,get:r}=Pe(t);let i=n.call(t,e);i?Fn(t,n,e):(e=g(e),i=n.call(t,e));const o=r?r.call(t,e):void 0,a=t.delete(e);return i&&I(t,"delete",e,void 0,o),a}function Lt(){const e=g(this),t=e.size!==0,n=ie(e)?new Map(e):new Set(e),r=e.clear();return t&&I(e,"clear",void 0,void 0,n),r}function pe(e,t){return function(r,i){const o=this,a=o.__v_raw,s=g(a),l=t?bt:e?mt:xt;return!e&&C(s,"iterate",B),a.forEach((d,c)=>r.call(i,l(d),l(c),o))}}function ge(e,t,n){return function(...r){const i=this.__v_raw,o=g(i),a=ie(o),s=e==="entries"||e===Symbol.iterator&&a,l=e==="keys"&&a,d=i[e](...r),c=n?bt:t?mt:xt;return!t&&C(o,"iterate",l?Ge:B),{next(){const{value:f,done:p}=d.next();return p?{value:f,done:p}:{value:s?[c(f[0]),c(f[1])]:c(f),done:p}},[Symbol.iterator](){return this}}}}function M(e){return function(...t){{const n=t[0]?`on key "${t[0]}" `:"";console.warn(`${mi(e)} operation ${n}failed: target is readonly.`,g(this))}return e==="delete"?!1:this}}function Ri(){const e={get(o){return ce(this,o)},get size(){return fe(this)},has:ue,add:Et,set:Pt,delete:Mt,clear:Lt,forEach:pe(!1,!1)},t={get(o){return ce(this,o,!1,!0)},get size(){return fe(this)},has:ue,add:Et,set:Pt,delete:Mt,clear:Lt,forEach:pe(!1,!0)},n={get(o){return ce(this,o,!0)},get size(){return fe(this,!0)},has(o){return ue.call(this,o,!0)},add:M("add"),set:M("set"),delete:M("delete"),clear:M("clear"),forEach:pe(!0,!1)},r={get(o){return ce(this,o,!0,!0)},get size(){return fe(this,!0)},has(o){return ue.call(this,o,!0)},add:M("add"),set:M("set"),delete:M("delete"),clear:M("clear"),forEach:pe(!0,!0)};return["keys","values","entries",Symbol.iterator].forEach(o=>{e[o]=ge(o,!1,!1),n[o]=ge(o,!0,!1),t[o]=ge(o,!1,!0),r[o]=ge(o,!0,!0)}),[e,n,t,r]}var[Di,Fi,Po,Mo]=Ri();function Dn(e,t){const n=e?Fi:Di;return(r,i,o)=>i==="__v_isReactive"?!e:i==="__v_isReadonly"?e:i==="__v_raw"?r:Reflect.get(Ae(n,i)&&i in r?n:r,i,o)}var Bi={get:Dn(!1)},Ni={get:Dn(!0)};function Fn(e,t,n){const r=g(n);if(r!==n&&t.call(e,r)){const i=On(e);console.warn(`Reactive ${i} contains both the raw and reactive versions of the same object${i==="Map"?" as keys":""}, which can lead to inconsistencies. Avoid differentiating between the raw and reactive versions of an object and only use the reactive version if possible.`)}}var Bn=new WeakMap,zi=new WeakMap,Nn=new WeakMap,Hi=new WeakMap;function Vi(e){switch(e){case"Object":case"Array":return 1;case"Map":case"Set":case"WeakMap":case"WeakSet":return 2;default:return 0}}function Wi(e){return e.__v_skip||!Object.isExtensible(e)?0:Vi(On(e))}function vt(e){return e&&e.__v_isReadonly?e:Hn(e,!1,Ti,Bi,Bn)}function zn(e){return Hn(e,!0,$i,Ni,Nn)}function Hn(e,t,n,r,i){if(!Ee(e))return console.warn(`value cannot be made reactive: ${String(e)}`),e;if(e.__v_raw&&!(t&&e.__v_isReactive))return e;const o=i.get(e);if(o)return o;const a=Wi(e);if(a===0)return e;const s=new Proxy(e,a===2?r:n);return i.set(e,s),s}function g(e){return e&&g(e.__v_raw)||e}function Ye(e){return!!(e&&e.__v_isRef===!0)}S("nextTick",()=>ct);S("dispatch",e=>re.bind(re,e));S("watch",(e,{evaluateLater:t,cleanup:n})=>(r,i)=>{let o=t(r),s=Ft(()=>{let l;return o(d=>l=d),l},i);n(s)});S("store",oi);S("data",e=>qt(e));S("root",e=>ke(e));S("refs",e=>(e._x_refs_proxy||(e._x_refs_proxy=se(Ki(e))),e._x_refs_proxy));function Ki(e){let t=[];return Y(e,n=>{n._x_refs&&t.push(n._x_refs)}),t}var Ie={};function Vn(e){return Ie[e]||(Ie[e]=0),++Ie[e]}function qi(e,t){return Y(e,n=>{if(n._x_ids&&n._x_ids[t])return!0})}function Ui(e,t){e._x_ids||(e._x_ids={}),e._x_ids[t]||(e._x_ids[t]=Vn(t))}S("id",(e,{cleanup:t})=>(n,r=null)=>{let i=`${n}${r?`-${r}`:""}`;return Ji(e,i,t,()=>{let o=qi(e,n),a=o?o._x_ids[n]:Vn(n);return r?`${n}-${a}-${r}`:`${n}-${a}`})});Se((e,t)=>{e._x_id&&(t._x_id=e._x_id)});function Ji(e,t,n,r){if(e._x_id||(e._x_id={}),e._x_id[t])return e._x_id[t];let i=r();return e._x_id[t]=i,n(()=>{delete e._x_id[t]}),i}S("el",e=>e);Wn("Focus","focus","focus");Wn("Persist","persist","persist");function Wn(e,t,n){S(t,r=>k(`You can't use [$${t}] without first installing the "${e}" plugin here: https://alpinejs.dev/plugins/${n}`,r))}b("modelable",(e,{expression:t},{effect:n,evaluateLater:r,cleanup:i})=>{let o=r(t),a=()=>{let c;return o(f=>c=f),c},s=r(`${t} = __placeholder`),l=c=>s(()=>{},{scope:{__placeholder:c}}),d=a();l(d),queueMicrotask(()=>{if(!e._x_model)return;e._x_removeModelListeners.default();let c=e._x_model.get,f=e._x_model.set,p=An({get(){return c()},set(v){f(v)}},{get(){return a()},set(v){l(v)}});i(p)})});b("teleport",(e,{modifiers:t,expression:n},{cleanup:r})=>{e.tagName.toLowerCase()!=="template"&&k("x-teleport can only be used on a <template> tag",e);let i=Ot(n),o=e.content.cloneNode(!0).firstElementChild;e._x_teleport=o,o._x_teleportBack=e,e.setAttribute("data-teleport-template",!0),o.setAttribute("data-teleport-target",!0),e._x_forwardEvents&&e._x_forwardEvents.forEach(s=>{o.addEventListener(s,l=>{l.stopPropagation(),e.dispatchEvent(new l.constructor(l.type,l))})}),ae(o,{},e);let a=(s,l,d)=>{d.includes("prepend")?l.parentNode.insertBefore(s,l):d.includes("append")?l.parentNode.insertBefore(s,l.nextSibling):l.appendChild(s)};x(()=>{a(o,i,t),j(()=>{E(o)})()}),e._x_teleportPutBack=()=>{let s=Ot(n);x(()=>{a(e._x_teleport,s,t)})},r(()=>x(()=>{o.remove(),X(o)}))});var Gi=document.createElement("div");function Ot(e){let t=j(()=>document.querySelector(e),()=>Gi)();return t||k(`Cannot find x-teleport element for selector: "${e}"`),t}var Kn=()=>{};Kn.inline=(e,{modifiers:t},{cleanup:n})=>{t.includes("self")?e._x_ignoreSelf=!0:e._x_ignore=!0,n(()=>{t.includes("self")?delete e._x_ignoreSelf:delete e._x_ignore})};b("ignore",Kn);b("effect",j((e,{expression:t},{effect:n})=>{n(w(e,t))}));function Xe(e,t,n,r){let i=e,o=l=>r(l),a={},s=(l,d)=>c=>d(l,c);if(n.includes("dot")&&(t=Yi(t)),n.includes("camel")&&(t=Xi(t)),n.includes("passive")&&(a.passive=!0),n.includes("capture")&&(a.capture=!0),n.includes("window")&&(i=window),n.includes("document")&&(i=document),n.includes("debounce")){let l=n[n.indexOf("debounce")+1]||"invalid-wait",d=we(l.split("ms")[0])?Number(l.split("ms")[0]):250;o=Cn(o,d)}if(n.includes("throttle")){let l=n[n.indexOf("throttle")+1]||"invalid-wait",d=we(l.split("ms")[0])?Number(l.split("ms")[0]):250;o=Sn(o,d)}return n.includes("prevent")&&(o=s(o,(l,d)=>{d.preventDefault(),l(d)})),n.includes("stop")&&(o=s(o,(l,d)=>{d.stopPropagation(),l(d)})),n.includes("once")&&(o=s(o,(l,d)=>{l(d),i.removeEventListener(t,o,a)})),(n.includes("away")||n.includes("outside"))&&(i=document,o=s(o,(l,d)=>{e.contains(d.target)||d.target.isConnected!==!1&&(e.offsetWidth<1&&e.offsetHeight<1||e._x_isShown!==!1&&l(d))})),n.includes("self")&&(o=s(o,(l,d)=>{d.target===e&&l(d)})),(Qi(t)||qn(t))&&(o=s(o,(l,d)=>{eo(d,n)||l(d)})),i.addEventListener(t,o,a),()=>{i.removeEventListener(t,o,a)}}function Yi(e){return e.replace(/-/g,".")}function Xi(e){return e.toLowerCase().replace(/-(\w)/g,(t,n)=>n.toUpperCase())}function we(e){return!Array.isArray(e)&&!isNaN(e)}function Zi(e){return[" ","_"].includes(e)?e:e.replace(/([a-z])([A-Z])/g,"$1-$2").replace(/[_\s]/,"-").toLowerCase()}function Qi(e){return["keydown","keyup"].includes(e)}function qn(e){return["contextmenu","click","mouse"].some(t=>e.includes(t))}function eo(e,t){let n=t.filter(o=>!["window","document","prevent","stop","once","capture","self","away","outside","passive"].includes(o));if(n.includes("debounce")){let o=n.indexOf("debounce");n.splice(o,we((n[o+1]||"invalid-wait").split("ms")[0])?2:1)}if(n.includes("throttle")){let o=n.indexOf("throttle");n.splice(o,we((n[o+1]||"invalid-wait").split("ms")[0])?2:1)}if(n.length===0||n.length===1&&It(e.key).includes(n[0]))return!1;const i=["ctrl","shift","alt","meta","cmd","super"].filter(o=>n.includes(o));return n=n.filter(o=>!i.includes(o)),!(i.length>0&&i.filter(a=>((a==="cmd"||a==="super")&&(a="meta"),e[`${a}Key`])).length===i.length&&(qn(e.type)||It(e.key).includes(n[0])))}function It(e){if(!e)return[];e=Zi(e);let t={ctrl:"control",slash:"/",space:" ",spacebar:" ",cmd:"meta",esc:"escape",up:"arrow-up",down:"arrow-down",left:"arrow-left",right:"arrow-right",period:".",comma:",",equal:"=",minus:"-",underscore:"_"};return t[e]=e,Object.keys(t).map(n=>{if(t[n]===e)return n}).filter(n=>n)}b("model",(e,{modifiers:t,expression:n},{effect:r,cleanup:i})=>{let o=e;t.includes("parent")&&(o=e.parentNode);let a=w(o,n),s;typeof n=="string"?s=w(o,`${n} = __placeholder`):typeof n=="function"&&typeof n()=="string"?s=w(o,`${n()} = __placeholder`):s=()=>{};let l=()=>{let p;return a(v=>p=v),jt(p)?p.get():p},d=p=>{let v;a(P=>v=P),jt(v)?v.set(p):s(()=>{},{scope:{__placeholder:p}})};typeof n=="string"&&e.type==="radio"&&x(()=>{e.hasAttribute("name")||e.setAttribute("name",n)});var c=e.tagName.toLowerCase()==="select"||["checkbox","radio"].includes(e.type)||t.includes("lazy")?"change":"input";let f=O?()=>{}:Xe(e,c,t,p=>{d(je(e,t,p,l()))});if(t.includes("fill")&&([void 0,null,""].includes(l())||ft(e)&&Array.isArray(l())||e.tagName.toLowerCase()==="select"&&e.multiple)&&d(je(e,t,{target:e},l())),e._x_removeModelListeners||(e._x_removeModelListeners={}),e._x_removeModelListeners.default=f,i(()=>e._x_removeModelListeners.default()),e.form){let p=Xe(e.form,"reset",[],v=>{ct(()=>e._x_model&&e._x_model.set(je(e,t,{target:e},l())))});i(()=>p())}e._x_model={get(){return l()},set(p){d(p)}},e._x_forceModelUpdate=p=>{p===void 0&&typeof n=="string"&&n.match(/\./)&&(p=""),window.fromModel=!0,x(()=>vn(e,"value",p)),delete window.fromModel},r(()=>{let p=l();t.includes("unintrusive")&&document.activeElement.isSameNode(e)||e._x_forceModelUpdate(p)})});function je(e,t,n,r){return x(()=>{if(n instanceof CustomEvent&&n.detail!==void 0)return n.detail!==null&&n.detail!==void 0?n.detail:n.target.value;if(ft(e))if(Array.isArray(r)){let i=null;return t.includes("number")?i=Te(n.target.value):t.includes("boolean")?i=me(n.target.value):i=n.target.value,n.target.checked?r.includes(i)?r:r.concat([i]):r.filter(o=>!to(o,i))}else return n.target.checked;else{if(e.tagName.toLowerCase()==="select"&&e.multiple)return t.includes("number")?Array.from(n.target.selectedOptions).map(i=>{let o=i.value||i.text;return Te(o)}):t.includes("boolean")?Array.from(n.target.selectedOptions).map(i=>{let o=i.value||i.text;return me(o)}):Array.from(n.target.selectedOptions).map(i=>i.value||i.text);{let i;return kn(e)?n.target.checked?i=n.target.value:i=r:i=n.target.value,t.includes("number")?Te(i):t.includes("boolean")?me(i):t.includes("trim")?i.trim():i}}})}function Te(e){let t=e?parseFloat(e):null;return no(t)?t:e}function to(e,t){return e==t}function no(e){return!Array.isArray(e)&&!isNaN(e)}function jt(e){return e!==null&&typeof e=="object"&&typeof e.get=="function"&&typeof e.set=="function"}b("cloak",e=>queueMicrotask(()=>x(()=>e.removeAttribute(G("cloak")))));pn(()=>`[${G("init")}]`);b("init",j((e,{expression:t},{evaluate:n})=>typeof t=="string"?!!t.trim()&&n(t,{},!1):n(t,{},!1)));b("text",(e,{expression:t},{effect:n,evaluateLater:r})=>{let i=r(t);n(()=>{i(o=>{x(()=>{e.textContent=o})})})});b("html",(e,{expression:t},{effect:n,evaluateLater:r})=>{let i=r(t);n(()=>{i(o=>{x(()=>{e.innerHTML=o,e._x_ignoreSelf=!0,E(e),delete e._x_ignoreSelf})})})});st(nn(":",rn(G("bind:"))));var Un=(e,{value:t,modifiers:n,expression:r,original:i},{effect:o,cleanup:a})=>{if(!t){let l={};si(l),w(e,r)(c=>{Pn(e,c,i)},{scope:l});return}if(t==="key")return ro(e,r);if(e._x_inlineBindings&&e._x_inlineBindings[t]&&e._x_inlineBindings[t].extract)return;let s=w(e,r);o(()=>s(l=>{l===void 0&&typeof r=="string"&&r.match(/\./)&&(l=""),x(()=>vn(e,t,l,n))})),a(()=>{e._x_undoAddedClasses&&e._x_undoAddedClasses(),e._x_undoAddedStyles&&e._x_undoAddedStyles()})};Un.inline=(e,{value:t,modifiers:n,expression:r})=>{t&&(e._x_inlineBindings||(e._x_inlineBindings={}),e._x_inlineBindings[t]={expression:r,extract:!1})};b("bind",Un);function ro(e,t){e._x_keyExpression=t}fn(()=>`[${G("data")}]`);b("data",(e,{expression:t},{cleanup:n})=>{if(io(e))return;t=t===""?"{}":t;let r={};Ne(r,e);let i={};di(i,r);let o=D(e,t,{scope:i});(o===void 0||o===!0)&&(o={}),Ne(o,e);let a=U(o);Ut(a);let s=ae(e,a);a.init&&D(e,a.init),n(()=>{a.destroy&&D(e,a.destroy),s()})});Se((e,t)=>{e._x_dataStack&&(t._x_dataStack=e._x_dataStack,t.setAttribute("data-has-alpine-state",!0))});function io(e){return O?Ue?!0:e.hasAttribute("data-has-alpine-state"):!1}b("show",(e,{modifiers:t,expression:n},{effect:r})=>{let i=w(e,n);e._x_doHide||(e._x_doHide=()=>{x(()=>{e.style.setProperty("display","none",t.includes("important")?"important":void 0)})}),e._x_doShow||(e._x_doShow=()=>{x(()=>{e.style.length===1&&e.style.display==="none"?e.removeAttribute("style"):e.style.removeProperty("display")})});let o=()=>{e._x_doHide(),e._x_isShown=!1},a=()=>{e._x_doShow(),e._x_isShown=!0},s=()=>setTimeout(a),l=Ke(f=>f?a():o(),f=>{typeof e._x_toggleAndCascadeWithTransitions=="function"?e._x_toggleAndCascadeWithTransitions(e,f,a,o):f?s():o()}),d,c=!0;r(()=>i(f=>{!c&&f===d||(t.includes("immediate")&&(f?s():o()),l(f),d=f,c=!1)}))});b("for",(e,{expression:t},{effect:n,cleanup:r})=>{let i=ao(t),o=w(e,i.items),a=w(e,e._x_keyExpression||"index");e._x_prevKeys=[],e._x_lookup={},n(()=>oo(e,i,o,a)),r(()=>{Object.values(e._x_lookup).forEach(s=>x(()=>{X(s),s.remove()})),delete e._x_prevKeys,delete e._x_lookup})});function oo(e,t,n,r){let i=a=>typeof a=="object"&&!Array.isArray(a),o=e;n(a=>{so(a)&&a>=0&&(a=Array.from(Array(a).keys(),u=>u+1)),a===void 0&&(a=[]);let s=e._x_lookup,l=e._x_prevKeys,d=[],c=[];if(i(a))a=Object.entries(a).map(([u,h])=>{let m=Tt(t,h,u,a);r(y=>{c.includes(y)&&k("Duplicate key on x-for",e),c.push(y)},{scope:{index:u,...m}}),d.push(m)});else for(let u=0;u<a.length;u++){let h=Tt(t,a[u],u,a);r(m=>{c.includes(m)&&k("Duplicate key on x-for",e),c.push(m)},{scope:{index:u,...h}}),d.push(h)}let f=[],p=[],v=[],P=[];for(let u=0;u<l.length;u++){let h=l[u];c.indexOf(h)===-1&&v.push(h)}l=l.filter(u=>!v.includes(u));let de="template";for(let u=0;u<c.length;u++){let h=c[u],m=l.indexOf(h);if(m===-1)l.splice(u,0,h),f.push([de,u]);else if(m!==u){let y=l.splice(u,1)[0],_=l.splice(m-1,1)[0];l.splice(u,0,_),l.splice(m,0,y),p.push([y,_])}else P.push(h);de=h}for(let u=0;u<v.length;u++){let h=v[u];h in s&&(x(()=>{X(s[h]),s[h].remove()}),delete s[h])}for(let u=0;u<p.length;u++){let[h,m]=p[u],y=s[h],_=s[m],H=document.createElement("div");x(()=>{_||k('x-for ":key" is undefined or invalid',o,m,s),_.after(H),y.after(_),_._x_currentIfEl&&_.after(_._x_currentIfEl),H.before(y),y._x_currentIfEl&&y.after(y._x_currentIfEl),H.remove()}),_._x_refreshXForScope(d[c.indexOf(m)])}for(let u=0;u<f.length;u++){let[h,m]=f[u],y=h==="template"?o:s[h];y._x_currentIfEl&&(y=y._x_currentIfEl);let _=d[m],H=c[m],Z=document.importNode(o.content,!0).firstElementChild,yt=U(_);ae(Z,yt,o),Z._x_refreshXForScope=Xn=>{Object.entries(Xn).forEach(([Zn,Qn])=>{yt[Zn]=Qn})},x(()=>{y.after(Z),j(()=>E(Z))()}),typeof H=="object"&&k("x-for key cannot be an object, it must be a string or an integer",o),s[H]=Z}for(let u=0;u<P.length;u++)s[P[u]]._x_refreshXForScope(d[c.indexOf(P[u])]);o._x_prevKeys=c})}function ao(e){let t=/,([^,\}\]]*)(?:,([^,\}\]]*))?$/,n=/^\s*\(|\)\s*$/g,r=/([\s\S]*?)\s+(?:in|of)\s+([\s\S]*)/,i=e.match(r);if(!i)return;let o={};o.items=i[2].trim();let a=i[1].replace(n,"").trim(),s=a.match(t);return s?(o.item=a.replace(t,"").trim(),o.index=s[1].trim(),s[2]&&(o.collection=s[2].trim())):o.item=a,o}function Tt(e,t,n,r){let i={};return/^\[.*\]$/.test(e.item)&&Array.isArray(t)?e.item.replace("[","").replace("]","").split(",").map(a=>a.trim()).forEach((a,s)=>{i[a]=t[s]}):/^\{.*\}$/.test(e.item)&&!Array.isArray(t)&&typeof t=="object"?e.item.replace("{","").replace("}","").split(",").map(a=>a.trim()).forEach(a=>{i[a]=t[a]}):i[e.item]=t,e.index&&(i[e.index]=n),e.collection&&(i[e.collection]=r),i}function so(e){return!Array.isArray(e)&&!isNaN(e)}function Jn(){}Jn.inline=(e,{expression:t},{cleanup:n})=>{let r=ke(e);r._x_refs||(r._x_refs={}),r._x_refs[t]=e,n(()=>delete r._x_refs[t])};b("ref",Jn);b("if",(e,{expression:t},{effect:n,cleanup:r})=>{e.tagName.toLowerCase()!=="template"&&k("x-if can only be used on a <template> tag",e);let i=w(e,t),o=()=>{if(e._x_currentIfEl)return e._x_currentIfEl;let s=e.content.cloneNode(!0).firstElementChild;return ae(s,{},e),x(()=>{e.after(s),j(()=>E(s))()}),e._x_currentIfEl=s,e._x_undoIf=()=>{x(()=>{X(s),s.remove()}),delete e._x_currentIfEl},s},a=()=>{e._x_undoIf&&(e._x_undoIf(),delete e._x_undoIf)};n(()=>i(s=>{s?o():a()})),r(()=>e._x_undoIf&&e._x_undoIf())});b("id",(e,{expression:t},{evaluate:n})=>{n(t).forEach(i=>Ui(e,i))});Se((e,t)=>{e._x_ids&&(t._x_ids=e._x_ids)});st(nn("@",rn(G("on:"))));b("on",j((e,{value:t,modifiers:n,expression:r},{cleanup:i})=>{let o=r?w(e,r):()=>{};e.tagName.toLowerCase()==="template"&&(e._x_forwardEvents||(e._x_forwardEvents=[]),e._x_forwardEvents.includes(t)||e._x_forwardEvents.push(t));let a=Xe(e,t,n,s=>{o(()=>{},{scope:{$event:s},params:[s]})});i(()=>a())}));Me("Collapse","collapse","collapse");Me("Intersect","intersect","intersect");Me("Focus","trap","focus");Me("Mask","mask","mask");function Me(e,t,n){b(t,r=>k(`You can't use [x-${t}] without first installing the "${e}" plugin here: https://alpinejs.dev/plugins/${n}`,r))}le.setEvaluator(Zt);le.setReactivityEngine({reactive:vt,effect:vi,release:yi,raw:g});var lo=le,Gn=lo;const co={async loginApi(e,t){try{const n=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:e,password:t})});if(!n.ok)throw new Error(`HTTP error! status: ${n.status}`);return await n.json()}catch(n){throw console.error("Login failed:",n),n}}},_e={username:"",password:"",isLoading:!1,error:null,response:null,isLoggedIn:!1,token:null,init(){this.isLoggedIn=!!localStorage.getItem("token"),this.token=localStorage.getItem("token")},async login(){if(this.isLoading=!0,this.error=null,!this.username||!this.username.trim()){this.error="Username is required",this.isLoading=!1;return}if(!this.password||!this.password.trim()){this.error="Password is required",this.isLoading=!1;return}try{const e=await co.loginApi(this.username,this.password);e.token?(this.token=e.token,localStorage.setItem("token",e.token),this.isLoggedIn=!0,window.location.href="/"):this.error=e.message||"Login failed. Please try again."}catch(e){console.error("Login error:",e),this.error="Login failed. Please try again."}finally{this.isLoading=!1}}},uo=localStorage.getItem("darkMode")==="true";uo?document.documentElement.classList.add("dark"):document.documentElement.classList.remove("dark");const Yn={sidebarOpen:!1,darkMode:!1,init(){typeof window<"u"&&window.innerWidth>=1024&&(this.sidebarOpen=!0),this.darkMode=localStorage.getItem("darkMode")==="true",this.applyTheme(),localStorage.getItem("darkMode")===null&&(this.darkMode=window.matchMedia("(prefers-color-scheme: dark)").matches,localStorage.setItem("darkMode",this.darkMode),this.applyTheme()),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",e=>{localStorage.getItem("darkMode")===null&&(this.darkMode=e.matches,localStorage.setItem("darkMode",this.darkMode),this.applyTheme())})},toggleDarkMode(){this.darkMode=!this.darkMode,localStorage.setItem("darkMode",this.darkMode),this.applyTheme()},applyTheme(){this.darkMode?document.documentElement.classList.add("dark"):document.documentElement.classList.remove("dark")}},Ze={cloneCommand:"git clone https://github.com/you/vanilla-webapp-framework.git",copyFeedback:"",carouselCurrent:0,carouselDots:[0,1,2,3],carouselTimer:null,init(){this.copyFeedback=""},initCarousel(){this.stopCarousel(),this.carouselCurrent=0,this.carouselTimer=setInterval(()=>{this.goSlide(this.carouselCurrent+1)},5e3)},stopCarousel(){this.carouselTimer&&(clearInterval(this.carouselTimer),this.carouselTimer=null)},goSlide(e){const t=this.carouselDots.length;this.carouselCurrent=(e%t+t)%t},prevSlide(){this.goSlide(this.carouselCurrent-1),this.restartCarousel()},nextSlide(){this.goSlide(this.carouselCurrent+1),this.restartCarousel()},restartCarousel(){this.stopCarousel(),this.carouselTimer=setInterval(()=>{this.goSlide(this.carouselCurrent+1)},5e3)},async copyCloneCommand(){var e;try{(e=navigator.clipboard)!=null&&e.writeText?(await navigator.clipboard.writeText(this.cloneCommand),this.copyFeedback="Copied!"):this.copyFeedback="Copy unavailable"}catch{this.copyFeedback="Copy failed"}setTimeout(()=>{this.copyFeedback=""},2e3)}},fo={appContext:null,isLoading:!1,error:null,response:null,token:null,init(e){this.appContext=e,this.isLoading=!1,this.error=null,this.response=null,this.token=localStorage.getItem("token")},async fetchProtectedData(){var e;if(!this.appContext||!this.token){this.error="Not logged in",(e=this.appContext)==null||e.logout();return}this.isLoading=!0,this.error=null;try{const t=await fetch("/api/data",{headers:{Authorization:`Bearer ${this.token}`}});t.ok?this.response=await t.json():(t.status===401?(this.error="Unauthorized",this.appContext.logout()):this.error=`Error: ${t.status}`,this.response=null)}catch{this.error="Failed to fetch data",this.appContext.logout()}finally{this.isLoading=!1}},async fetchPublicData(){this.isLoading=!0,this.error=null;try{const e=await fetch("/api/public");e.ok?this.response=await e.json():(this.error=`Error: ${e.status}`,this.response=null)}catch{this.error="Failed to fetch data"}finally{this.isLoading=!1}}},po={abc:0,isLoading:!1,appContext:null,init(e){this.appContext=e,console.log("Test page controller initialized"),this.isLoading=!1},async ttt(){this.isLoading=!0,console.log("ttt called, abc is:",this.abc),await new Promise(e=>setTimeout(e,500)),console.log("ttt finished"),this.isLoading=!1}},go={async registerApi(e,t){const n=await fetch("/api/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:e,password:t})}),r=await n.json().catch(()=>({}));if(!n.ok)throw new Error(r.message||`Registration failed (${n.status})`);return r}},ho={appContext:null,username:"",password:"",confirmPassword:"",isLoading:!1,error:null,success:null,init(e){this.appContext=e,this.username="",this.password="",this.confirmPassword="",this.isLoading=!1,this.error=null,this.success=null},async register(){if(this.isLoading=!0,this.error=null,this.success=null,!this.username||!this.username.trim()){this.error="Username is required",this.isLoading=!1;return}if(!this.password||this.password.length<6){this.error="Password must be at least 6 characters",this.isLoading=!1;return}if(this.password!==this.confirmPassword){this.error="Passwords do not match",this.isLoading=!1;return}try{const e=await go.registerApi(this.username,this.password);e.message==="User created successfully"?(this.success="Account created successfully! You can now login.",this.username="",this.password="",this.confirmPassword="",setTimeout(()=>{this.appContext.loadPage("login-register-container","login")},2e3)):this.error=e.message||"Registration failed. Please try again."}catch(e){console.error("Registration failed:",e),this.error=e.message||"Registration failed. Please try again."}finally{this.isLoading=!1}}},xo=`<!-- Sidebar Navigation -->
<div x-data="{ hoveredItem: null }">
  <aside 
    class="fixed inset-y-0 left-0 z-10 w-16 hover:w-64 transform transition-all duration-300 ease-in-out bg-white dark:bg-gray-800 shadow-lg overflow-hidden group"
    :class="{ '-translate-x-full': !menuController.sidebarOpen, 'translate-x-0': menuController.sidebarOpen }">
    
    <div class="flex flex-col h-full">
      <!-- Logo -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-center lg:justify-start">
        <svg class="h-8 w-8 text-indigo-600 dark:text-indigo-400 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span class="text-xl font-bold text-gray-800 dark:text-white ml-2 hidden group-hover:inline-block whitespace-nowrap">Vanilla App</span>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        <!-- Dashboard -->
        <a href="#" @click.prevent="loadPage('view-container', 'landingpage');"
           @mouseenter="hoveredItem = 'dashboard'" @mouseleave="hoveredItem = null"
           class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap">Dashboard</span>
        </a>

        <!-- Analytics -->
        <a href="#" @click.prevent="loadPage('view-container', 'testpage');"
           @mouseenter="hoveredItem = 'analytics'" @mouseleave="hoveredItem = null"
           class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap">Analytics</span>
        </a>

        <!-- Settings -->
        <a href="#" 
           @mouseenter="hoveredItem = 'settings'" @mouseleave="hoveredItem = null"
           class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap">Settings</span>
        </a>

        <!-- Profile -->
        <a href="#" 
           @mouseenter="hoveredItem = 'profile'" @mouseleave="hoveredItem = null"
           class="flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap">Profile</span>
        </a>

        <!-- Logout Button -->
        <button @click="logout"
           @mouseenter="hoveredItem = 'logout'" @mouseleave="hoveredItem = null"
           class="w-full flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-red-100 dark:hover:bg-red-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap">Logout</span>
        </button>
      </nav>

      <!-- Dark Mode Toggle -->
      <div class="p-2 border-t border-gray-200 dark:border-gray-700">
        <button @click="menuController.toggleDarkMode()"
               @mouseenter="hoveredItem = 'darkmode'" @mouseleave="hoveredItem = null"
               class="w-full flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <div class="w-5 h-5 flex items-center justify-center">
            <!-- Sun icon for light mode -->
            <svg x-show="!menuController.darkMode" class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <!-- Moon icon for dark mode -->
            <svg x-show="menuController.darkMode" class="w-5 h-5 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </div>
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="menuController.darkMode ? 'Light Mode' : 'Dark Mode'"></span>
        </button>
      </div>
    </div>
  </aside>

  <!-- Mobile menuController Toggle -->
  <div class="fixed top-0 left-0 z-20 m-4 lg:hidden">
    <button @click="menuController.sidebarOpen = !menuController.sidebarOpen" class="p-2 bg-white dark:bg-gray-800 rounded-md shadow-md text-gray-800 dark:text-white focus:outline-none">
      <svg x-show="!menuController.sidebarOpen" class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <svg x-show="menuController.sidebarOpen" class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <!-- Page Content Overlay when sidebar is open on mobile -->
  <div 
    x-show="menuController.sidebarOpen" 
    @click="menuController.sidebarOpen = false" 
    class="fixed inset-0 z-5 bg-black opacity-50 lg:hidden"
    x-cloak>
  </div>
</div>
`,mo=`<!-- Login Form Partial -->

<div x-show="!isLoggedIn" class="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6" >
    <div class="space-y-4">
        <div class="text-center">
            <a href="#" @click.prevent="showWelcomePage()"
               class="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300">
                ← Back to welcome
            </a>
        </div>
        <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">Vanilla WebApp Demo</h1>
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
            <input type="text" 
                    x-model="loginController.username" 
                    class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                    :disabled="loginController.isLoading">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <input type="password" 
                    x-model="loginController.password" 
                    class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                    :disabled="loginController.isLoading">
        </div>
        <button @click="loginController.login()" 
                class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors duration-200 disabled:opacity-50"
                :disabled="loginController.isLoading">
            <span x-show="!loginController.isLoading">Login</span>
            <span x-show="loginController.isLoading">Loading...</span>
        </button>

        <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">or continue with</span>
            </div>
        </div>

        <div class="space-y-3">
            <button type="button"
                    @click="startSocialLogin('google')"
                    :class="oauthProviders.includes('google')
                        ? 'hover:bg-gray-50 dark:hover:bg-gray-600 cursor-pointer'
                        : 'opacity-60 cursor-not-allowed'"
                    class="flex items-center justify-center gap-3 w-full py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 transition-colors duration-200">
                <svg class="w-5 h-5 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span class="text-gray-700 dark:text-gray-200 font-medium">Google</span>
            </button>

            <button type="button"
                    @click="startSocialLogin('facebook')"
                    :class="oauthProviders.includes('facebook')
                        ? 'hover:bg-[#166FE5] cursor-pointer'
                        : 'opacity-60 cursor-not-allowed'"
                    class="flex items-center justify-center gap-3 w-full py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md bg-[#1877F2] transition-colors duration-200">
                <svg class="w-5 h-5 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill="#ffffff" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                <span class="text-white font-medium">Facebook</span>
            </button>
        </div>

        <p x-show="oauthProviders.length === 0"
           class="text-xs text-center text-gray-500 dark:text-gray-400">
            Social login requires provider keys in <code class="text-indigo-600 dark:text-indigo-400">.env</code>.
            Restart Flask after adding them.
        </p>

        <div class="text-center mt-4">
            <a href="#" @click.prevent="loadPage('login-register-container', 'user_registry');" 
                class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300">
                Don't have an account? Register
            </a>
        </div>
        
        <!-- Error Message -->
        <div x-show="loginController.error" 
            class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
            x-text="loginController.error">
        </div>
        
        <!-- Response Data -->
        <div x-show="loginController.response" class="mt-4">
            <h2 class="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Response:</h2>
            <pre class="bg-gray-100 dark:bg-gray-700 p-4 rounded-md overflow-x-auto text-gray-800 dark:text-gray-200" x-text="JSON.stringify(loginController.response, null, 2)"></pre>
        </div>
    </div>
</div>
`,bo=`<!-- User Registration Page -->

<div class="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="space-y-4">
        <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">Create an Account</h1>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
            <input 
                type="text" 
                x-model="currentPage.username" 
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                :disabled="currentPage.isLoading">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <input 
                type="password" 
                x-model="currentPage.password" 
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                :disabled="currentPage.isLoading">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Confirm Password</label>
            <input 
                type="password" 
                x-model="currentPage.confirmPassword" 
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                :disabled="currentPage.isLoading">
        </div>
        
        <button 
            @click="currentPage.register()" 
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading || !currentPage.username || !currentPage.password || currentPage.password !== currentPage.confirmPassword || currentPage.password.length < 6">
            <span x-show="!currentPage.isLoading">Register</span>
            <span x-show="currentPage.isLoading">Processing...</span>
        </button>
        
        <div class="text-center mt-4">
            <a href="#" @click.prevent="loadPage('login-register-container', 'login');" 
                class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300">
                Already have an account? Login
            </a>
        </div>
        
        <!-- Error Message -->
        <div 
            x-show="currentPage.error" 
            class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
            x-text="currentPage.error">
        </div>
        
        <!-- Success Message -->
        <div 
            x-show="currentPage.success" 
            class="mt-4 p-4 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md" 
            x-text="currentPage.success">
        </div>
    </div>
</div>
`,vo=`<!-- Public welcome page — loaded into #public-container -->
<div class="bg-gray-50 text-gray-900 antialiased dark:bg-gray-950 dark:text-gray-100 min-h-screen">

    <header class="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm" aria-hidden="true">V</div>
                <span class="font-semibold text-gray-900 dark:text-white">Vanilla WebApp</span>
            </div>
            <nav class="hidden sm:flex items-center gap-6 text-sm text-gray-600 dark:text-gray-300" aria-label="Welcome page sections">
                <a href="#carousel" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">See it work</a>
                <a href="#features" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Features</a>
                <a href="#partners" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Partners</a>
            </nav>
            <div class="flex items-center gap-3">
                <button type="button"
                        @click="menuController.toggleDarkMode()"
                        aria-label="Toggle dark mode"
                        class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition">
                    <svg x-show="menuController.darkMode" x-cloak class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.36 6.36l-.71-.71M6.34 6.34l-.71-.71m12.02 0l-.71.71M6.34 17.66l-.71.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                    <svg x-show="!menuController.darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
                </button>
                <button type="button"
                        @click="showLoginPage()"
                        class="inline-flex items-center gap-2 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                    Sign In
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
                </button>
            </div>
        </div>
    </header>

    <section class="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 text-white">
        <div class="absolute inset-0 opacity-[0.07]"
             style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 28px 28px;"></div>
        <div class="relative max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16 text-center">
            <p class="inline-flex items-center gap-2 text-indigo-100 text-xs font-medium tracking-wide uppercase mb-4 bg-white/10 border border-white/15 rounded-full px-3 py-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                Open-source starter kit
            </p>
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight max-w-3xl mx-auto leading-tight">
                Ship your entrepreneur SaaS faster
            </h1>
            <p class="mt-4 text-base sm:text-lg text-indigo-100 max-w-2xl mx-auto">
                Flask REST API, Alpine.js SPA, JWT + OAuth, SEO modes, and Docker — a production-ready starter so you focus on your idea, not boilerplate.
            </p>
            <div class="mt-7 inline-flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 max-w-full px-2">
                <code class="flex items-center text-left text-xs sm:text-sm bg-indigo-950/40 text-emerald-300 px-4 py-2.5 rounded-lg border border-white/20 font-mono overflow-x-auto">
                    <span class="text-indigo-300/70 mr-2 select-none">$</span><span x-text="welcomeController.cloneCommand"></span>
                </code>
                <button type="button"
                        @click="welcomeController.copyCloneCommand()"
                        class="shrink-0 inline-flex items-center justify-center gap-2 bg-white text-indigo-700 font-semibold px-6 py-2.5 rounded-lg hover:bg-indigo-50 transition shadow-lg text-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                    <span x-text="welcomeController.copyFeedback || 'Copy command'"></span>
                </button>
            </div>
            <div class="mt-7 flex flex-wrap justify-center gap-x-6 gap-y-1 text-xs sm:text-sm text-indigo-200">
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>Auth &amp; OAuth ready</span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>Vite + Tailwind</span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>Alembic migrations</span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>CI + Docker</span>
            </div>
        </div>
    </section>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12 lg:py-16">
        <div class="lg:grid lg:grid-cols-[1fr_300px] lg:gap-10 items-start">

            <main class="min-w-0 space-y-14">
                <section id="carousel">
                    <div class="mb-6 lg:text-left text-center">
                        <p class="text-xs uppercase tracking-widest text-indigo-600 dark:text-indigo-400 font-semibold">See it work</p>
                        <h2 class="mt-1 text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Built for real products</h2>
                        <p class="mt-2 text-gray-600 dark:text-gray-400">Everything below ships in the box — no add-ons required.</p>
                    </div>
                    <div class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
                        <div class="aspect-video relative bg-slate-900">
                            <div class="absolute inset-0 transition-opacity duration-500" :class="welcomeController.carouselCurrent === 0 ? 'opacity-100' : 'opacity-0'">
                                <div class="h-full flex flex-col">
                                    <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
                                        <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                                        <span class="ml-3 text-[11px] text-slate-400 font-mono">localhost:5173 → /api → :5000</span>
                                    </div>
                                    <div class="flex-1 grid grid-cols-2">
                                        <div class="bg-slate-900 p-5 font-mono text-[11px] sm:text-xs leading-relaxed text-slate-300 overflow-hidden">
                                            <p><span class="text-violet-400">vite</span> <span class="text-slate-500">v5</span> <span class="text-emerald-400">ready</span></p>
                                            <p class="text-slate-500">➜ Local: http://localhost:5173</p>
                                            <p class="text-slate-500">➜ proxy /api → :5000</p>
                                            <p class="mt-2 text-indigo-300">GET /api/public 200</p>
                                            <p class="text-indigo-300">GET /api/data 200</p>
                                        </div>
                                        <div class="bg-gradient-to-br from-indigo-600 to-violet-700 p-6 flex flex-col justify-center text-white">
                                            <span class="text-xs uppercase tracking-widest text-indigo-200">Dev workflow</span>
                                            <p class="mt-1 text-xl sm:text-2xl font-bold leading-snug">Dual-server, one origin</p>
                                            <p class="mt-2 text-sm text-indigo-100">Vite proxies <code class="bg-white/15 px-1 rounded">/api</code> to Flask — zero CORS pain.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="absolute inset-0 transition-opacity duration-500" :class="welcomeController.carouselCurrent === 1 ? 'opacity-100' : 'opacity-0'">
                                <div class="h-full flex flex-col">
                                    <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
                                        <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                                        <span class="ml-3 text-[11px] text-slate-400 font-mono">/api/auth/google/login</span>
                                    </div>
                                    <div class="flex-1 bg-slate-900 flex items-center justify-center p-6">
                                        <div class="w-full max-w-xs space-y-3">
                                            <div class="h-9 rounded-md bg-slate-800 border border-slate-700"></div>
                                            <div class="h-9 rounded-md bg-slate-800 border border-slate-700"></div>
                                            <div class="h-9 rounded-md bg-indigo-600 flex items-center justify-center text-white text-xs font-semibold">Sign in</div>
                                            <div class="flex items-center gap-2 text-[10px] text-slate-500"><span class="flex-1 h-px bg-slate-700"></span>or<span class="flex-1 h-px bg-slate-700"></span></div>
                                            <div class="h-9 rounded-md bg-white flex items-center justify-center text-slate-700 text-xs font-medium gap-2"><span class="w-3.5 h-3.5 rounded-full bg-gradient-to-br from-blue-500 to-red-500" aria-hidden="true"></span>Continue with Google</div>
                                            <div class="h-9 rounded-md bg-[#1877F2] flex items-center justify-center text-white text-xs font-medium">Continue with Facebook</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="absolute inset-0 transition-opacity duration-500" :class="welcomeController.carouselCurrent === 2 ? 'opacity-100' : 'opacity-0'">
                                <div class="h-full flex flex-col">
                                    <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
                                        <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                                        <span class="ml-3 text-[11px] text-slate-400 font-mono">localhost:5000/docs</span>
                                    </div>
                                    <div class="flex-1 bg-slate-50 dark:bg-slate-900 p-5 space-y-2 overflow-hidden">
                                        <div class="flex items-center gap-2"><span class="text-[10px] font-bold text-white bg-emerald-600 px-2 py-0.5 rounded">GET</span><span class="text-xs font-mono text-slate-600 dark:text-slate-300">/api/public</span></div>
                                        <div class="flex items-center gap-2"><span class="text-[10px] font-bold text-white bg-indigo-600 px-2 py-0.5 rounded">POST</span><span class="text-xs font-mono text-slate-600 dark:text-slate-300">/api/login</span></div>
                                        <div class="flex items-center gap-2"><span class="text-[10px] font-bold text-white bg-emerald-600 px-2 py-0.5 rounded">GET</span><span class="text-xs font-mono text-slate-600 dark:text-slate-300">/api/data 🔒</span></div>
                                        <div class="flex items-center gap-2"><span class="text-[10px] font-bold text-white bg-indigo-600 px-2 py-0.5 rounded">POST</span><span class="text-xs font-mono text-slate-600 dark:text-slate-300">/api/register</span></div>
                                        <p class="pt-2 text-xs text-slate-500">Interactive Swagger UI — every route documented.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="absolute inset-0 transition-opacity duration-500" :class="welcomeController.carouselCurrent === 3 ? 'opacity-100' : 'opacity-0'">
                                <div class="h-full flex flex-col">
                                    <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
                                        <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
                                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
                                        <span class="ml-3 text-[11px] text-slate-400 font-mono">docker build · APP_PROFILE=production</span>
                                    </div>
                                    <div class="flex-1 bg-slate-900 p-5 font-mono text-[11px] sm:text-xs leading-relaxed text-slate-300">
                                        <p><span class="text-emerald-400">✓</span> npm run build → backend/static/</p>
                                        <p><span class="text-emerald-400">✓</span> flask serves SPA fallback</p>
                                        <p><span class="text-emerald-400">✓</span> single Docker image</p>
                                        <p class="mt-3 text-slate-500"># one server, /api + /* from :5000</p>
                                        <p class="text-indigo-300">Listening on 0.0.0.0:5000</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800">
                            <button type="button" @click="welcomeController.prevSlide()" class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition" aria-label="Previous slide">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                            </button>
                            <div class="flex gap-2">
                                <button type="button"
                                        @click="welcomeController.goSlide(0); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 0 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        aria-label="Go to slide 1"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(1); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 1 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        aria-label="Go to slide 2"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(2); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 2 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        aria-label="Go to slide 3"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(3); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 3 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        aria-label="Go to slide 4"></button>
                            </div>
                            <button type="button" @click="welcomeController.nextSlide()" class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition" aria-label="Next slide">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                            </button>
                        </div>
                    </div>
                </section>

                <section id="features">
                    <div class="mb-8 lg:text-left text-center">
                        <p class="text-xs uppercase tracking-widest text-indigo-600 dark:text-indigo-400 font-semibold">Why this stack</p>
                        <h2 class="mt-1 text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Why founders choose it</h2>
                    </div>
                    <div class="grid sm:grid-cols-3 gap-6">
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white">Backend-first</h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm">Models, blueprints, pytest coverage, and Alembic before you touch UI.</p>
                        </article>
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8l-4 4 4 4m10-8l4 4-4 4M14 4l-4 16"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white">Vanilla frontend</h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm">Alpine.js controllers + Handlebars templates — no framework lock-in.</p>
                        </article>
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white">SEO fork-ready</h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm">auth-first or public-first modes with /robots.txt and page metadata.</p>
                        </article>
                    </div>
                </section>
            </main>

            <aside id="partners" class="mt-12 lg:mt-0 lg:sticky lg:top-20 space-y-5">
                <p class="hidden lg:block text-xs uppercase tracking-widest text-gray-400 dark:text-gray-500 font-semibold mb-6">Partners</p>

                <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
                    <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                        <h3 class="text-sm font-bold text-gray-900 dark:text-white">Recommended tools</h3>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Affiliate picks for your stack</p>
                    </div>
                    <div class="divide-y divide-gray-100 dark:divide-gray-800">
                        <a href="https://www.digitalocean.com/" target="_blank" rel="noopener noreferrer sponsored" class="block p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition group border-l-2 border-l-transparent hover:border-l-amber-400">
                            <div class="flex gap-3">
                                <div class="w-11 h-11 rounded-lg bg-gradient-to-br from-blue-400 to-blue-700 shrink-0 flex items-center justify-center text-white text-xs font-bold" aria-hidden="true">DO</div>
                                <div class="min-w-0">
                                    <p class="text-[10px] font-semibold uppercase text-amber-600 tracking-wider">Hosting</p>
                                    <p class="font-semibold text-sm text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 leading-snug transition">DigitalOcean App Platform</p>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">$200 credit · managed SSL</p>
                                </div>
                            </div>
                        </a>
                        <a href="https://www.namecheap.com/" target="_blank" rel="noopener noreferrer sponsored" class="block p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition group border-l-2 border-l-transparent hover:border-l-amber-400">
                            <div class="flex gap-3">
                                <div class="w-11 h-11 rounded-lg bg-gradient-to-br from-orange-400 to-red-600 shrink-0 flex items-center justify-center text-white text-xs font-bold" aria-hidden="true">NC</div>
                                <div class="min-w-0">
                                    <p class="text-[10px] font-semibold uppercase text-amber-600 tracking-wider">Domain</p>
                                    <p class="font-semibold text-sm text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 leading-snug transition">Namecheap .com</p>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">DNS ready for OAuth redirects</p>
                                </div>
                            </div>
                        </a>
                    </div>
                    <p class="px-4 py-2 text-[10px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-800/40 border-t border-gray-100 dark:border-gray-800">Contains affiliate links</p>
                </div>

                <div class="bg-gray-50 dark:bg-gray-900/40 border border-dashed border-gray-300 dark:border-gray-700 rounded-2xl overflow-hidden" aria-label="Ad slot medium rectangle">
                    <div class="px-3 py-2 border-b border-dashed border-gray-300 dark:border-gray-700">
                        <span class="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Sponsored</span>
                    </div>
                    <div class="flex flex-col items-center justify-center py-14 px-4">
                        <span class="text-xs font-mono text-gray-400 uppercase">Ad slot</span>
                        <span class="text-sm text-gray-500 dark:text-gray-400 mt-1">Medium rectangle</span>
                        <span class="text-xs text-gray-400 mt-0.5">300 × 250</span>
                    </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-900/40 border border-dashed border-gray-300 dark:border-gray-700 rounded-2xl overflow-hidden" aria-label="Ad slot display banner">
                    <div class="flex flex-col items-center justify-center py-8 px-4">
                        <span class="text-xs font-mono text-gray-400 uppercase">Ad slot</span>
                        <span class="text-sm text-gray-500 dark:text-gray-400 mt-1">Display banner</span>
                        <span class="text-xs text-gray-400 mt-0.5">300 × 100</span>
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <footer class="bg-gray-900 dark:bg-black text-gray-300 border-t border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
            <div class="flex flex-col sm:flex-row items-center justify-between gap-6">
                <div class="text-center sm:text-left">
                    <div class="flex items-center gap-2 justify-center sm:justify-start">
                        <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xs" aria-hidden="true">V</div>
                        <span class="font-semibold text-white">Vanilla WebApp Framework</span>
                    </div>
                    <p class="mt-2 text-sm text-gray-400">Fork it, set your <code class="text-gray-300 bg-gray-800 px-1.5 py-0.5 rounded text-xs">.env</code>, and ship.</p>
                </div>
                <div class="flex items-center gap-4">
                    <a href="https://github.com/" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 text-sm text-gray-300 hover:text-white transition">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.26.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.085 1.84 1.237 1.84 1.237 1.07 1.835 2.807 1.305 3.492.998.108-.776.42-1.305.762-1.605-2.665-.303-5.467-1.332-5.467-5.93 0-1.31.467-2.38 1.235-3.22-.124-.303-.535-1.523.117-3.176 0 0 1.008-.322 3.3 1.23a11.5 11.5 0 016.003 0c2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.806 5.624-5.479 5.92.43.372.823 1.102.823 2.222 0 1.605-.015 2.9-.015 3.295 0 .32.216.694.825.576C20.565 21.795 24 17.297 24 12c0-6.63-5.37-12-12-12z"/></svg>
                        View on GitHub
                    </a>
                    <button type="button"
                            @click="welcomeController.copyCloneCommand()"
                            class="inline-flex items-center gap-2 bg-indigo-500 hover:bg-indigo-400 text-white font-medium px-5 py-2.5 rounded-lg transition text-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span x-text="welcomeController.copyFeedback || 'Copy clone command'"></span>
                    </button>
                </div>
            </div>
            <div class="mt-8 pt-6 border-t border-gray-800 text-center text-xs text-gray-500">
                © 2026 Vanilla WebApp Framework · Built with Flask, Alpine.js &amp; Tailwind
            </div>
        </div>
    </footer>
</div>
`,yo=`<div class="space-y-4 max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">

    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">Vanilla WebApp Demo 2</h1>
    <button @click="logout" 
            class="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors duration-200">
        Logout
    </button>
    <button @click="currentPage.fetchProtectedData()" 
            class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading">Fetch Protected Data</span>
        <span x-show="currentPage.isLoading">Loading...</span>
    </button>
    <button @click="currentPage.fetchPublicData()" 
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading">Fetch Public Data</span>
        <span x-show="currentPage.isLoading">Loading...</span>
    </button>

    <button @click="loadPage('view-container', 'testpage');" 
            class="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading">Load Test Page</span>
        <span x-show="currentPage.isLoading">Loading...</span>
    </button>

    <!-- Error Message -->
    <div x-show="currentPage.error" 
        class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
        x-text="currentPage.error">
    </div>

    <!-- Response Data -->
    <div x-show="currentPage.response" class="mt-4">
        <h2 class="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Response:</h2>
        <pre class="bg-gray-100 dark:bg-gray-700 p-4 rounded-md overflow-x-auto text-gray-800 dark:text-gray-200" x-text="JSON.stringify(currentPage.response, null, 2)"></pre>
    </div>

</div>
`,wo=`<button @click="currentPage.ttt(); loadPage('view-container', 'landingpage');" 
        x-init="currentPage.abc = 27;"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50"
        :disabled="currentPage.isLoading">
    <span x-show="!currentPage.isLoading">Load Landing Page</span>
    <span x-show="currentPage.isLoading">Loading...</span>
</button>
`,he="Vanilla WebApp Framework — lightweight Flask and Alpine.js starter for entrepreneur solutions.",V={menu:{template:xo,controller:Yn,seo:{visibility:"app",title:"Menu — Vanilla WebApp Demo"}},login:{template:mo,controller:_e,seo:{visibility:"auth",title:"Login — Vanilla WebApp Demo",description:he}},user_registry:{template:bo,controller:ho,seo:{visibility:"auth",title:"Register — Vanilla WebApp Demo",description:he}},welcome:{template:vo,controller:Ze,seo:{visibility:"public",title:"Vanilla WebApp Framework — Ship your SaaS faster",description:he}},landingpage:{template:yo,controller:fo,seo:{visibility:"app",title:"Vanilla WebApp Demo",description:he}},testpage:{template:wo,controller:po,seo:{visibility:"app",title:"Test Page — Vanilla WebApp Demo"}}},L="auth-first",_o=new Set(["auth-first","public-first"]),ko=new Set(["public","app","auth"]);function Co(e={},t=L){const n=_o.has(t)?t:"auth-first";return e.visibility&&ko.has(e.visibility)?e.visibility:n==="public-first"?"public":"app"}function So(e){return e==="public"}function $t(e,t){if(t==null||t==="")return;let n=document.querySelector(`meta[name="${e}"]`);n||(n=document.createElement("meta"),n.setAttribute("name",e),document.head.appendChild(n)),n.setAttribute("content",t)}function Rt(e,t){if(!t)return;let n=document.querySelector(`link[rel="${e}"]`);n||(n=document.createElement("link"),n.setAttribute("rel",e),document.head.appendChild(n)),n.setAttribute("href",t)}function W(e={},t=L){const n=Co(e,t),r=So(n);e.title&&(document.title=e.title),e.description&&$t("description",e.description),$t("robots",r?"index, follow":"noindex, nofollow"),e.canonical?Rt("canonical",e.canonical):r&&Rt("canonical",window.location.href.split("#")[0])}function Ao(e){const t=window.location.hash.slice(1);if(!t)return;const n=new URLSearchParams(t),r=n.get("token"),i=n.get("auth_error");window.history.replaceState(null,"",window.location.pathname+window.location.search),r?(localStorage.setItem("token",r),e.isLoggedIn=!0):i&&(_e.error=decodeURIComponent(i),e.showLogin=!0,W(V.login.seo,L))}const Eo=()=>{const e={isLoggedIn:!!localStorage.getItem("token"),showLogin:!1,oauthProviders:[],currentPage:{},menuController:Yn,loginController:_e,welcomeController:Ze,showLoginPage(){this.showLogin=!0,this.refreshOAuthProviders(),W(V.login.seo,L)},showWelcomePage(){this.showLogin=!1,W(V.welcome.seo,L)},applyInitialSeo(){this.isLoggedIn?W(V.landingpage.seo,L):W(V.welcome.seo,L)},async refreshOAuthProviders(){try{const t=await fetch("/api/auth/providers");t.ok&&(this.oauthProviders=await t.json())}catch(t){console.error("Failed to load OAuth providers:",t)}},isOAuthEnabled(t){return this.oauthProviders.includes(t)},startSocialLogin(t){if(!this.isOAuthEnabled(t)){const n=t.toUpperCase();_e.error=`${t.charAt(0).toUpperCase()}${t.slice(1)} login is not configured. Add ${n}_CLIENT_ID and ${n}_CLIENT_SECRET to .env, then restart Flask.`;return}window.location.href=`/api/auth/${t}/login`},loadPage(t,n){const r=V[n];if(!r){console.error(`Unknown page: ${n}`);return}const i=document.getElementById(t);if(!i){console.error(`Element not found: ${t}`);return}window.Alpine.mutateDom(()=>{i.innerHTML=r.template}),this.currentPage=Object.assign({},r.controller),typeof this.currentPage.init=="function"&&this.currentPage.init(this),Array.from(i.children).forEach(o=>{window.Alpine.initTree(o)}),t==="view-container"&&r.seo&&W(r.seo,L),n==="login"&&this.refreshOAuthProviders(),n==="welcome"&&Ze.initCarousel()},bootApp(){this.loadPage("menu-container","menu"),this.loadPage("login-register-container","login"),this.loadPage("public-container","welcome"),this.loadPage("view-container","landingpage"),this.applyInitialSeo()},logout(){localStorage.removeItem("token"),window.location.href="/"}};return e.menuController.init(),e.loginController.init(),e.welcomeController.init(),e.refreshOAuthProviders(),Ao(e),window.menuController=e.menuController,window.loginController=e.loginController,window.welcomeController=e.welcomeController,e};window.Alpine=Gn;window.spaApp=Eo();Gn.start();window.spaApp.bootApp();
