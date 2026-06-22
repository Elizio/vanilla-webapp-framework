(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))r(o);new MutationObserver(o=>{for(const i of o)if(i.type==="childList")for(const a of i.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&r(a)}).observe(document,{childList:!0,subtree:!0});function n(o){const i={};return o.integrity&&(i.integrity=o.integrity),o.referrerPolicy&&(i.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?i.credentials="include":o.crossOrigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(o){if(o.ep)return;o.ep=!0;const i=n(o);fetch(o.href,i)}})();var je=!1,Be=!1,B=[],$e=-1;function ar(e){sr(e)}function sr(e){B.includes(e)||B.push(e),cr()}function lr(e){let t=B.indexOf(e);t!==-1&&t>$e&&B.splice(t,1)}function cr(){!Be&&!je&&(je=!0,queueMicrotask(dr))}function dr(){je=!1,Be=!0;for(let e=0;e<B.length;e++)B[e](),$e=e;B.length=0,$e=-1,Be=!1}var q,H,J,$t,Ue=!0;function ur(e){Ue=!1,e(),Ue=!0}function pr(e){q=e.reactive,J=e.release,H=t=>e.effect(t,{scheduler:n=>{Ue?ar(n):n()}}),$t=e.raw}function St(e){H=e}function fr(e){let t=()=>{};return[r=>{let o=H(r);return e._x_effects||(e._x_effects=new Set,e._x_runEffects=()=>{e._x_effects.forEach(i=>i())}),e._x_effects.add(o),t=()=>{o!==void 0&&(e._x_effects.delete(o),J(o))},o},()=>{t()}]}function Ut(e,t){let n=!0,r,o=H(()=>{let i=e();JSON.stringify(i),n?r=i:queueMicrotask(()=>{t(i,r),r=i}),n=!1});return()=>J(o)}var Wt=[],Vt=[],Ht=[];function gr(e){Ht.push(e)}function nt(e,t){typeof t=="function"?(e._x_cleanups||(e._x_cleanups=[]),e._x_cleanups.push(t)):(t=e,Vt.push(t))}function Kt(e){Wt.push(e)}function zt(e,t,n){e._x_attributeCleanups||(e._x_attributeCleanups={}),e._x_attributeCleanups[t]||(e._x_attributeCleanups[t]=[]),e._x_attributeCleanups[t].push(n)}function Gt(e,t){e._x_attributeCleanups&&Object.entries(e._x_attributeCleanups).forEach(([n,r])=>{(t===void 0||t.includes(n))&&(r.forEach(o=>o()),delete e._x_attributeCleanups[n])})}function hr(e){var t,n;for((t=e._x_effects)==null||t.forEach(lr);(n=e._x_cleanups)!=null&&n.length;)e._x_cleanups.pop()()}var rt=new MutationObserver(st),ot=!1;function it(){rt.observe(document,{subtree:!0,childList:!0,attributes:!0,attributeOldValue:!0}),ot=!0}function qt(){xr(),rt.disconnect(),ot=!1}var ee=[];function xr(){let e=rt.takeRecords();ee.push(()=>e.length>0&&st(e));let t=ee.length;queueMicrotask(()=>{if(ee.length===t)for(;ee.length>0;)ee.shift()()})}function x(e){if(!ot)return e();qt();let t=e();return it(),t}var at=!1,be=[];function mr(){at=!0}function br(){at=!1,st(be),be=[]}function st(e){if(at){be=be.concat(e);return}let t=[],n=new Set,r=new Map,o=new Map;for(let i=0;i<e.length;i++)if(!e[i].target._x_ignoreMutationObserver&&(e[i].type==="childList"&&(e[i].removedNodes.forEach(a=>{a.nodeType===1&&a._x_marker&&n.add(a)}),e[i].addedNodes.forEach(a=>{if(a.nodeType===1){if(n.has(a)){n.delete(a);return}a._x_marker||t.push(a)}})),e[i].type==="attributes")){let a=e[i].target,s=e[i].attributeName,l=e[i].oldValue,c=()=>{r.has(a)||r.set(a,[]),r.get(a).push({name:s,value:a.getAttribute(s)})},d=()=>{o.has(a)||o.set(a,[]),o.get(a).push(s)};a.hasAttribute(s)&&l===null?c():a.hasAttribute(s)?(d(),c()):d()}o.forEach((i,a)=>{Gt(a,i)}),r.forEach((i,a)=>{Wt.forEach(s=>s(a,i))});for(let i of n)t.some(a=>a.contains(i))||Vt.forEach(a=>a(i));for(let i of t)i.isConnected&&Ht.forEach(a=>a(i));t=null,n=null,r=null,o=null}function Jt(e){return le(z(e))}function se(e,t,n){return e._x_dataStack=[t,...z(n||e)],()=>{e._x_dataStack=e._x_dataStack.filter(r=>r!==t)}}function z(e){return e._x_dataStack?e._x_dataStack:typeof ShadowRoot=="function"&&e instanceof ShadowRoot?z(e.host):e.parentNode?z(e.parentNode):[]}function le(e){return new Proxy({objects:e},vr)}var vr={ownKeys({objects:e}){return Array.from(new Set(e.flatMap(t=>Object.keys(t))))},has({objects:e},t){return t==Symbol.unscopables?!1:e.some(n=>Object.prototype.hasOwnProperty.call(n,t)||Reflect.has(n,t))},get({objects:e},t,n){return t=="toJSON"?wr:Reflect.get(e.find(r=>Reflect.has(r,t))||{},t,n)},set({objects:e},t,n,r){const o=e.find(a=>Object.prototype.hasOwnProperty.call(a,t))||e[e.length-1],i=Object.getOwnPropertyDescriptor(o,t);return i!=null&&i.set&&(i!=null&&i.get)?i.set.call(r,n)||!0:Reflect.set(o,t,n)}};function wr(){return Reflect.ownKeys(this).reduce((t,n)=>(t[n]=Reflect.get(this,n),t),{})}function Qt(e){let t=r=>typeof r=="object"&&!Array.isArray(r)&&r!==null,n=(r,o="")=>{Object.entries(Object.getOwnPropertyDescriptors(r)).forEach(([i,{value:a,enumerable:s}])=>{if(s===!1||a===void 0||typeof a=="object"&&a!==null&&a.__v_skip)return;let l=o===""?i:`${o}.${i}`;typeof a=="object"&&a!==null&&a._x_interceptor?r[i]=a.initialize(e,l,i):t(a)&&a!==r&&!(a instanceof Element)&&n(a,l)})};return n(e)}function Xt(e,t=()=>{}){let n={initialValue:void 0,_x_interceptor:!0,initialize(r,o,i){return e(this.initialValue,()=>yr(r,o),a=>We(r,o,a),o,i)}};return t(n),r=>{if(typeof r=="object"&&r!==null&&r._x_interceptor){let o=n.initialize.bind(n);n.initialize=(i,a,s)=>{let l=r.initialize(i,a,s);return n.initialValue=l,o(i,a,s)}}else n.initialValue=r;return n}}function yr(e,t){return t.split(".").reduce((n,r)=>n[r],e)}function We(e,t,n){if(typeof t=="string"&&(t=t.split(".")),t.length===1)e[t[0]]=n;else{if(t.length===0)throw error;return e[t[0]]||(e[t[0]]={}),We(e[t[0]],t.slice(1),n)}}var Yt={};function C(e,t){Yt[e]=t}function Ve(e,t){let n=_r(t);return Object.entries(Yt).forEach(([r,o])=>{Object.defineProperty(e,`$${r}`,{get(){return o(t,n)},enumerable:!1})}),e}function _r(e){let[t,n]=on(e),r={interceptor:Xt,...t};return nt(e,n),r}function kr(e,t,n,...r){try{return n(...r)}catch(o){ae(o,e,t)}}function ae(e,t,n=void 0){e=Object.assign(e??{message:"No error message given."},{el:t,expression:n}),console.warn(`Alpine Expression Error: ${e.message}

${n?'Expression: "'+n+`"

`:""}`,t),setTimeout(()=>{throw e},0)}var xe=!0;function Zt(e){let t=xe;xe=!1;let n=e();return xe=t,n}function $(e,t,n={}){let r;return y(e,t)(o=>r=o,n),r}function y(...e){return en(...e)}var en=tn;function Sr(e){en=e}function tn(e,t){let n={};Ve(n,e);let r=[n,...z(e)],o=typeof t=="function"?Cr(r,t):Ar(r,t,e);return kr.bind(null,e,t,o)}function Cr(e,t){return(n=()=>{},{scope:r={},params:o=[]}={})=>{let i=t.apply(le([r,...e]),o);ve(n,i)}}var Re={};function Er(e,t){if(Re[e])return Re[e];let n=Object.getPrototypeOf(async function(){}).constructor,r=/^[\n\s]*if.*\(.*\)/.test(e.trim())||/^(let|const)\s/.test(e.trim())?`(async()=>{ ${e} })()`:e,i=(()=>{try{let a=new n(["__self","scope"],`with (scope) { __self.result = ${r} }; __self.finished = true; return __self.result;`);return Object.defineProperty(a,"name",{value:`[Alpine] ${e}`}),a}catch(a){return ae(a,t,e),Promise.resolve()}})();return Re[e]=i,i}function Ar(e,t,n){let r=Er(t,n);return(o=()=>{},{scope:i={},params:a=[]}={})=>{r.result=void 0,r.finished=!1;let s=le([i,...e]);if(typeof r=="function"){let l=r(r,s).catch(c=>ae(c,n,t));r.finished?(ve(o,r.result,s,a,n),r.result=void 0):l.then(c=>{ve(o,c,s,a,n)}).catch(c=>ae(c,n,t)).finally(()=>r.result=void 0)}}}function ve(e,t,n,r,o){if(xe&&typeof t=="function"){let i=t.apply(n,r);i instanceof Promise?i.then(a=>ve(e,a,n,r)).catch(a=>ae(a,o,t)):e(i)}else typeof t=="object"&&t instanceof Promise?t.then(i=>e(i)):e(t)}var lt="x-";function Q(e=""){return lt+e}function Pr(e){lt=e}var we={};function b(e,t){return we[e]=t,{before(n){if(!we[n]){console.warn(String.raw`Cannot find directive \`${n}\`. \`${e}\` will use the default order of execution`);return}const r=j.indexOf(n);j.splice(r>=0?r:j.indexOf("DEFAULT"),0,e)}}}function Or(e){return Object.keys(we).includes(e)}function ct(e,t,n){if(t=Array.from(t),e._x_virtualDirectives){let i=Object.entries(e._x_virtualDirectives).map(([s,l])=>({name:s,value:l})),a=nn(i);i=i.map(s=>a.find(l=>l.name===s.name)?{name:`x-bind:${s.name}`,value:`"${s.value}"`}:s),t=t.concat(i)}let r={};return t.map(ln((i,a)=>r[i]=a)).filter(dn).map(Lr(r,n)).sort(Rr).map(i=>Ir(e,i))}function nn(e){return Array.from(e).map(ln()).filter(t=>!dn(t))}var He=!1,re=new Map,rn=Symbol();function Tr(e){He=!0;let t=Symbol();rn=t,re.set(t,[]);let n=()=>{for(;re.get(t).length;)re.get(t).shift()();re.delete(t)},r=()=>{He=!1,n()};e(n),r()}function on(e){let t=[],n=s=>t.push(s),[r,o]=fr(e);return t.push(o),[{Alpine:ce,effect:r,cleanup:n,evaluateLater:y.bind(y,e),evaluate:$.bind($,e)},()=>t.forEach(s=>s())]}function Ir(e,t){let n=()=>{},r=we[t.type]||n,[o,i]=on(e);zt(e,t.original,i);let a=()=>{e._x_ignore||e._x_ignoreSelf||(r.inline&&r.inline(e,t,o),r=r.bind(r,e,t,o),He?re.get(rn).push(r):r())};return a.runCleanups=i,a}var an=(e,t)=>({name:n,value:r})=>(n.startsWith(e)&&(n=n.replace(e,t)),{name:n,value:r}),sn=e=>e;function ln(e=()=>{}){return({name:t,value:n})=>{let{name:r,value:o}=cn.reduce((i,a)=>a(i),{name:t,value:n});return r!==t&&e(r,t),{name:r,value:o}}}var cn=[];function dt(e){cn.push(e)}function dn({name:e}){return un().test(e)}var un=()=>new RegExp(`^${lt}([^:^.]+)\\b`);function Lr(e,t){return({name:n,value:r})=>{let o=n.match(un()),i=n.match(/:([a-zA-Z0-9\-_:]+)/),a=n.match(/\.[^.\]]+(?=[^\]]*$)/g)||[],s=t||e[n]||n;return{type:o?o[1]:null,value:i?i[1]:null,modifiers:a.map(l=>l.replace(".","")),expression:r,original:s}}}var Ke="DEFAULT",j=["ignore","ref","data","id","anchor","bind","init","for","model","modelable","transition","show","if",Ke,"teleport"];function Rr(e,t){let n=j.indexOf(e.type)===-1?Ke:e.type,r=j.indexOf(t.type)===-1?Ke:t.type;return j.indexOf(n)-j.indexOf(r)}function oe(e,t,n={}){e.dispatchEvent(new CustomEvent(t,{detail:n,bubbles:!0,composed:!0,cancelable:!0}))}function V(e,t){if(typeof ShadowRoot=="function"&&e instanceof ShadowRoot){Array.from(e.children).forEach(o=>V(o,t));return}let n=!1;if(t(e,()=>n=!0),n)return;let r=e.firstElementChild;for(;r;)V(r,t),r=r.nextElementSibling}function k(e,...t){console.warn(`Alpine Warning: ${e}`,...t)}var Ct=!1;function Mr(){Ct&&k("Alpine has already been initialized on this page. Calling Alpine.start() more than once can cause problems."),Ct=!0,document.body||k("Unable to initialize. Trying to load Alpine before `<body>` is available. Did you forget to add `defer` in Alpine's `<script>` tag?"),oe(document,"alpine:init"),oe(document,"alpine:initializing"),it(),gr(t=>T(t,V)),nt(t=>Y(t)),Kt((t,n)=>{ct(t,n).forEach(r=>r())});let e=t=>!Ee(t.parentElement,!0);Array.from(document.querySelectorAll(gn().join(","))).filter(e).forEach(t=>{T(t)}),oe(document,"alpine:initialized"),setTimeout(()=>{jr()})}var ut=[],pn=[];function fn(){return ut.map(e=>e())}function gn(){return ut.concat(pn).map(e=>e())}function hn(e){ut.push(e)}function xn(e){pn.push(e)}function Ee(e,t=!1){return X(e,n=>{if((t?gn():fn()).some(o=>n.matches(o)))return!0})}function X(e,t){if(e){if(t(e))return e;if(e._x_teleportBack&&(e=e._x_teleportBack),!!e.parentElement)return X(e.parentElement,t)}}function Dr(e){return fn().some(t=>e.matches(t))}var mn=[];function Nr(e){mn.push(e)}var Fr=1;function T(e,t=V,n=()=>{}){X(e,r=>r._x_ignore)||Tr(()=>{t(e,(r,o)=>{r._x_marker||(n(r,o),mn.forEach(i=>i(r,o)),ct(r,r.attributes).forEach(i=>i()),r._x_ignore||(r._x_marker=Fr++),r._x_ignore&&o())})})}function Y(e,t=V){t(e,n=>{hr(n),Gt(n),delete n._x_marker})}function jr(){[["ui","dialog",["[x-dialog], [x-popover]"]],["anchor","anchor",["[x-anchor]"]],["sort","sort",["[x-sort]"]]].forEach(([t,n,r])=>{Or(n)||r.some(o=>{if(document.querySelector(o))return k(`found "${o}", but missing ${t} plugin`),!0})})}var ze=[],pt=!1;function ft(e=()=>{}){return queueMicrotask(()=>{pt||setTimeout(()=>{Ge()})}),new Promise(t=>{ze.push(()=>{e(),t()})})}function Ge(){for(pt=!1;ze.length;)ze.shift()()}function Br(){pt=!0}function gt(e,t){return Array.isArray(t)?Et(e,t.join(" ")):typeof t=="object"&&t!==null?$r(e,t):typeof t=="function"?gt(e,t()):Et(e,t)}function Et(e,t){let n=o=>o.split(" ").filter(i=>!e.classList.contains(i)).filter(Boolean),r=o=>(e.classList.add(...o),()=>{e.classList.remove(...o)});return t=t===!0?t="":t||"",r(n(t))}function $r(e,t){let n=s=>s.split(" ").filter(Boolean),r=Object.entries(t).flatMap(([s,l])=>l?n(s):!1).filter(Boolean),o=Object.entries(t).flatMap(([s,l])=>l?!1:n(s)).filter(Boolean),i=[],a=[];return o.forEach(s=>{e.classList.contains(s)&&(e.classList.remove(s),a.push(s))}),r.forEach(s=>{e.classList.contains(s)||(e.classList.add(s),i.push(s))}),()=>{a.forEach(s=>e.classList.add(s)),i.forEach(s=>e.classList.remove(s))}}function Ae(e,t){return typeof t=="object"&&t!==null?Ur(e,t):Wr(e,t)}function Ur(e,t){let n={};return Object.entries(t).forEach(([r,o])=>{n[r]=e.style[r],r.startsWith("--")||(r=Vr(r)),e.style.setProperty(r,o)}),setTimeout(()=>{e.style.length===0&&e.removeAttribute("style")}),()=>{Ae(e,n)}}function Wr(e,t){let n=e.getAttribute("style",t);return e.setAttribute("style",t),()=>{e.setAttribute("style",n||"")}}function Vr(e){return e.replace(/([a-z])([A-Z])/g,"$1-$2").toLowerCase()}function qe(e,t=()=>{}){let n=!1;return function(){n?t.apply(this,arguments):(n=!0,e.apply(this,arguments))}}b("transition",(e,{value:t,modifiers:n,expression:r},{evaluate:o})=>{typeof r=="function"&&(r=o(r)),r!==!1&&(!r||typeof r=="boolean"?Kr(e,n,t):Hr(e,r,t))});function Hr(e,t,n){bn(e,gt,""),{enter:o=>{e._x_transition.enter.during=o},"enter-start":o=>{e._x_transition.enter.start=o},"enter-end":o=>{e._x_transition.enter.end=o},leave:o=>{e._x_transition.leave.during=o},"leave-start":o=>{e._x_transition.leave.start=o},"leave-end":o=>{e._x_transition.leave.end=o}}[n](t)}function Kr(e,t,n){bn(e,Ae);let r=!t.includes("in")&&!t.includes("out")&&!n,o=r||t.includes("in")||["enter"].includes(n),i=r||t.includes("out")||["leave"].includes(n);t.includes("in")&&!r&&(t=t.filter((h,m)=>m<t.indexOf("out"))),t.includes("out")&&!r&&(t=t.filter((h,m)=>m>t.indexOf("out")));let a=!t.includes("opacity")&&!t.includes("scale"),s=a||t.includes("opacity"),l=a||t.includes("scale"),c=s?0:1,d=l?te(t,"scale",95)/100:1,p=te(t,"delay",0)/1e3,f=te(t,"origin","center"),v="opacity, transform",I=te(t,"duration",150)/1e3,de=te(t,"duration",75)/1e3,u="cubic-bezier(0.4, 0.0, 0.2, 1)";o&&(e._x_transition.enter.during={transformOrigin:f,transitionDelay:`${p}s`,transitionProperty:v,transitionDuration:`${I}s`,transitionTimingFunction:u},e._x_transition.enter.start={opacity:c,transform:`scale(${d})`},e._x_transition.enter.end={opacity:1,transform:"scale(1)"}),i&&(e._x_transition.leave.during={transformOrigin:f,transitionDelay:`${p}s`,transitionProperty:v,transitionDuration:`${de}s`,transitionTimingFunction:u},e._x_transition.leave.start={opacity:1,transform:"scale(1)"},e._x_transition.leave.end={opacity:c,transform:`scale(${d})`})}function bn(e,t,n={}){e._x_transition||(e._x_transition={enter:{during:n,start:n,end:n},leave:{during:n,start:n,end:n},in(r=()=>{},o=()=>{}){Je(e,t,{during:this.enter.during,start:this.enter.start,end:this.enter.end},r,o)},out(r=()=>{},o=()=>{}){Je(e,t,{during:this.leave.during,start:this.leave.start,end:this.leave.end},r,o)}})}window.Element.prototype._x_toggleAndCascadeWithTransitions=function(e,t,n,r){const o=document.visibilityState==="visible"?requestAnimationFrame:setTimeout;let i=()=>o(n);if(t){e._x_transition&&(e._x_transition.enter||e._x_transition.leave)?e._x_transition.enter&&(Object.entries(e._x_transition.enter.during).length||Object.entries(e._x_transition.enter.start).length||Object.entries(e._x_transition.enter.end).length)?e._x_transition.in(n):i():e._x_transition?e._x_transition.in(n):i();return}e._x_hidePromise=e._x_transition?new Promise((a,s)=>{e._x_transition.out(()=>{},()=>a(r)),e._x_transitioning&&e._x_transitioning.beforeCancel(()=>s({isFromCancelledTransition:!0}))}):Promise.resolve(r),queueMicrotask(()=>{let a=vn(e);a?(a._x_hideChildren||(a._x_hideChildren=[]),a._x_hideChildren.push(e)):o(()=>{let s=l=>{let c=Promise.all([l._x_hidePromise,...(l._x_hideChildren||[]).map(s)]).then(([d])=>d==null?void 0:d());return delete l._x_hidePromise,delete l._x_hideChildren,c};s(e).catch(l=>{if(!l.isFromCancelledTransition)throw l})})})};function vn(e){let t=e.parentNode;if(t)return t._x_hidePromise?t:vn(t)}function Je(e,t,{during:n,start:r,end:o}={},i=()=>{},a=()=>{}){if(e._x_transitioning&&e._x_transitioning.cancel(),Object.keys(n).length===0&&Object.keys(r).length===0&&Object.keys(o).length===0){i(),a();return}let s,l,c;zr(e,{start(){s=t(e,r)},during(){l=t(e,n)},before:i,end(){s(),c=t(e,o)},after:a,cleanup(){l(),c()}})}function zr(e,t){let n,r,o,i=qe(()=>{x(()=>{n=!0,r||t.before(),o||(t.end(),Ge()),t.after(),e.isConnected&&t.cleanup(),delete e._x_transitioning})});e._x_transitioning={beforeCancels:[],beforeCancel(a){this.beforeCancels.push(a)},cancel:qe(function(){for(;this.beforeCancels.length;)this.beforeCancels.shift()();i()}),finish:i},x(()=>{t.start(),t.during()}),Br(),requestAnimationFrame(()=>{if(n)return;let a=Number(getComputedStyle(e).transitionDuration.replace(/,.*/,"").replace("s",""))*1e3,s=Number(getComputedStyle(e).transitionDelay.replace(/,.*/,"").replace("s",""))*1e3;a===0&&(a=Number(getComputedStyle(e).animationDuration.replace("s",""))*1e3),x(()=>{t.before()}),r=!0,requestAnimationFrame(()=>{n||(x(()=>{t.end()}),Ge(),setTimeout(e._x_transitioning.finish,a+s),o=!0)})})}function te(e,t,n){if(e.indexOf(t)===-1)return n;const r=e[e.indexOf(t)+1];if(!r||t==="scale"&&isNaN(r))return n;if(t==="duration"||t==="delay"){let o=r.match(/([0-9]+)ms/);if(o)return o[1]}return t==="origin"&&["top","right","left","center","bottom"].includes(e[e.indexOf(t)+2])?[r,e[e.indexOf(t)+2]].join(" "):r}var R=!1;function D(e,t=()=>{}){return(...n)=>R?t(...n):e(...n)}function Gr(e){return(...t)=>R&&e(...t)}var wn=[];function Pe(e){wn.push(e)}function qr(e,t){wn.forEach(n=>n(e,t)),R=!0,yn(()=>{T(t,(n,r)=>{r(n,()=>{})})}),R=!1}var Qe=!1;function Jr(e,t){t._x_dataStack||(t._x_dataStack=e._x_dataStack),R=!0,Qe=!0,yn(()=>{Qr(t)}),R=!1,Qe=!1}function Qr(e){let t=!1;T(e,(r,o)=>{V(r,(i,a)=>{if(t&&Dr(i))return a();t=!0,o(i,a)})})}function yn(e){let t=H;St((n,r)=>{let o=t(n);return J(o),()=>{}}),e(),St(t)}function _n(e,t,n,r=[]){switch(e._x_bindings||(e._x_bindings=q({})),e._x_bindings[t]=n,t=r.includes("camel")?oo(t):t,t){case"value":Xr(e,n);break;case"style":Zr(e,n);break;case"class":Yr(e,n);break;case"selected":case"checked":eo(e,t,n);break;default:kn(e,t,n);break}}function Xr(e,t){if(En(e))e.attributes.value===void 0&&(e.value=t),window.fromModel&&(typeof t=="boolean"?e.checked=me(e.value)===t:e.checked=At(e.value,t));else if(ht(e))Number.isInteger(t)?e.value=t:!Array.isArray(t)&&typeof t!="boolean"&&![null,void 0].includes(t)?e.value=String(t):Array.isArray(t)?e.checked=t.some(n=>At(n,e.value)):e.checked=!!t;else if(e.tagName==="SELECT")ro(e,t);else{if(e.value===t)return;e.value=t===void 0?"":t}}function Yr(e,t){e._x_undoAddedClasses&&e._x_undoAddedClasses(),e._x_undoAddedClasses=gt(e,t)}function Zr(e,t){e._x_undoAddedStyles&&e._x_undoAddedStyles(),e._x_undoAddedStyles=Ae(e,t)}function eo(e,t,n){kn(e,t,n),no(e,t,n)}function kn(e,t,n){[null,void 0,!1].includes(n)&&ao(t)?e.removeAttribute(t):(Sn(t)&&(n=t),to(e,t,n))}function to(e,t,n){e.getAttribute(t)!=n&&e.setAttribute(t,n)}function no(e,t,n){e[t]!==n&&(e[t]=n)}function ro(e,t){const n=[].concat(t).map(r=>r+"");Array.from(e.options).forEach(r=>{r.selected=n.includes(r.value)})}function oo(e){return e.toLowerCase().replace(/-(\w)/g,(t,n)=>n.toUpperCase())}function At(e,t){return e==t}function me(e){return[1,"1","true","on","yes",!0].includes(e)?!0:[0,"0","false","off","no",!1].includes(e)?!1:e?!!e:null}var io=new Set(["allowfullscreen","async","autofocus","autoplay","checked","controls","default","defer","disabled","formnovalidate","inert","ismap","itemscope","loop","multiple","muted","nomodule","novalidate","open","playsinline","readonly","required","reversed","selected","shadowrootclonable","shadowrootdelegatesfocus","shadowrootserializable"]);function Sn(e){return io.has(e)}function ao(e){return!["aria-pressed","aria-checked","aria-expanded","aria-selected"].includes(e)}function so(e,t,n){return e._x_bindings&&e._x_bindings[t]!==void 0?e._x_bindings[t]:Cn(e,t,n)}function lo(e,t,n,r=!0){if(e._x_bindings&&e._x_bindings[t]!==void 0)return e._x_bindings[t];if(e._x_inlineBindings&&e._x_inlineBindings[t]!==void 0){let o=e._x_inlineBindings[t];return o.extract=r,Zt(()=>$(e,o.expression))}return Cn(e,t,n)}function Cn(e,t,n){let r=e.getAttribute(t);return r===null?typeof n=="function"?n():n:r===""?!0:Sn(t)?!![t,"true"].includes(r):r}function ht(e){return e.type==="checkbox"||e.localName==="ui-checkbox"||e.localName==="ui-switch"}function En(e){return e.type==="radio"||e.localName==="ui-radio"}function An(e,t){var n;return function(){var r=this,o=arguments,i=function(){n=null,e.apply(r,o)};clearTimeout(n),n=setTimeout(i,t)}}function Pn(e,t){let n;return function(){let r=this,o=arguments;n||(e.apply(r,o),n=!0,setTimeout(()=>n=!1,t))}}function On({get:e,set:t},{get:n,set:r}){let o=!0,i,a=H(()=>{let s=e(),l=n();if(o)r(Me(s)),o=!1;else{let c=JSON.stringify(s),d=JSON.stringify(l);c!==i?r(Me(s)):c!==d&&t(Me(l))}i=JSON.stringify(e()),JSON.stringify(n())});return()=>{J(a)}}function Me(e){return typeof e=="object"?JSON.parse(JSON.stringify(e)):e}function co(e){(Array.isArray(e)?e:[e]).forEach(n=>n(ce))}var N={},Pt=!1;function uo(e,t){if(Pt||(N=q(N),Pt=!0),t===void 0)return N[e];N[e]=t,Qt(N[e]),typeof t=="object"&&t!==null&&t.hasOwnProperty("init")&&typeof t.init=="function"&&N[e].init()}function po(){return N}var Tn={};function fo(e,t){let n=typeof t!="function"?()=>t:t;return e instanceof Element?In(e,n()):(Tn[e]=n,()=>{})}function go(e){return Object.entries(Tn).forEach(([t,n])=>{Object.defineProperty(e,t,{get(){return(...r)=>n(...r)}})}),e}function In(e,t,n){let r=[];for(;r.length;)r.pop()();let o=Object.entries(t).map(([a,s])=>({name:a,value:s})),i=nn(o);return o=o.map(a=>i.find(s=>s.name===a.name)?{name:`x-bind:${a.name}`,value:`"${a.value}"`}:a),ct(e,o,n).map(a=>{r.push(a.runCleanups),a()}),()=>{for(;r.length;)r.pop()()}}var Ln={};function ho(e,t){Ln[e]=t}function xo(e,t){return Object.entries(Ln).forEach(([n,r])=>{Object.defineProperty(e,n,{get(){return(...o)=>r.bind(t)(...o)},enumerable:!1})}),e}var mo={get reactive(){return q},get release(){return J},get effect(){return H},get raw(){return $t},version:"3.14.9",flushAndStopDeferringMutations:br,dontAutoEvaluateFunctions:Zt,disableEffectScheduling:ur,startObservingMutations:it,stopObservingMutations:qt,setReactivityEngine:pr,onAttributeRemoved:zt,onAttributesAdded:Kt,closestDataStack:z,skipDuringClone:D,onlyDuringClone:Gr,addRootSelector:hn,addInitSelector:xn,interceptClone:Pe,addScopeToNode:se,deferMutations:mr,mapAttributes:dt,evaluateLater:y,interceptInit:Nr,setEvaluator:Sr,mergeProxies:le,extractProp:lo,findClosest:X,onElRemoved:nt,closestRoot:Ee,destroyTree:Y,interceptor:Xt,transition:Je,setStyles:Ae,mutateDom:x,directive:b,entangle:On,throttle:Pn,debounce:An,evaluate:$,initTree:T,nextTick:ft,prefixed:Q,prefix:Pr,plugin:co,magic:C,store:uo,start:Mr,clone:Jr,cloneNode:qr,bound:so,$data:Jt,watch:Ut,walk:V,data:ho,bind:fo},ce=mo;function bo(e,t){const n=Object.create(null),r=e.split(",");for(let o=0;o<r.length;o++)n[r[o]]=!0;return o=>!!n[o]}var vo=Object.freeze({}),wo=Object.prototype.hasOwnProperty,Oe=(e,t)=>wo.call(e,t),U=Array.isArray,ie=e=>Rn(e)==="[object Map]",yo=e=>typeof e=="string",xt=e=>typeof e=="symbol",Te=e=>e!==null&&typeof e=="object",_o=Object.prototype.toString,Rn=e=>_o.call(e),Mn=e=>Rn(e).slice(8,-1),mt=e=>yo(e)&&e!=="NaN"&&e[0]!=="-"&&""+parseInt(e,10)===e,ko=e=>{const t=Object.create(null);return n=>t[n]||(t[n]=e(n))},So=ko(e=>e.charAt(0).toUpperCase()+e.slice(1)),Dn=(e,t)=>e!==t&&(e===e||t===t),Xe=new WeakMap,ne=[],E,W=Symbol("iterate"),Ye=Symbol("Map key iterate");function Co(e){return e&&e._isEffect===!0}function Eo(e,t=vo){Co(e)&&(e=e.raw);const n=Oo(e,t);return t.lazy||n(),n}function Ao(e){e.active&&(Nn(e),e.options.onStop&&e.options.onStop(),e.active=!1)}var Po=0;function Oo(e,t){const n=function(){if(!n.active)return e();if(!ne.includes(n)){Nn(n);try{return Io(),ne.push(n),E=n,e()}finally{ne.pop(),Fn(),E=ne[ne.length-1]}}};return n.id=Po++,n.allowRecurse=!!t.allowRecurse,n._isEffect=!0,n.active=!0,n.raw=e,n.deps=[],n.options=t,n}function Nn(e){const{deps:t}=e;if(t.length){for(let n=0;n<t.length;n++)t[n].delete(e);t.length=0}}var G=!0,bt=[];function To(){bt.push(G),G=!1}function Io(){bt.push(G),G=!0}function Fn(){const e=bt.pop();G=e===void 0?!0:e}function S(e,t,n){if(!G||E===void 0)return;let r=Xe.get(e);r||Xe.set(e,r=new Map);let o=r.get(n);o||r.set(n,o=new Set),o.has(E)||(o.add(E),E.deps.push(o),E.options.onTrack&&E.options.onTrack({effect:E,target:e,type:t,key:n}))}function M(e,t,n,r,o,i){const a=Xe.get(e);if(!a)return;const s=new Set,l=d=>{d&&d.forEach(p=>{(p!==E||p.allowRecurse)&&s.add(p)})};if(t==="clear")a.forEach(l);else if(n==="length"&&U(e))a.forEach((d,p)=>{(p==="length"||p>=r)&&l(d)});else switch(n!==void 0&&l(a.get(n)),t){case"add":U(e)?mt(n)&&l(a.get("length")):(l(a.get(W)),ie(e)&&l(a.get(Ye)));break;case"delete":U(e)||(l(a.get(W)),ie(e)&&l(a.get(Ye)));break;case"set":ie(e)&&l(a.get(W));break}const c=d=>{d.options.onTrigger&&d.options.onTrigger({effect:d,target:e,key:n,type:t,newValue:r,oldValue:o,oldTarget:i}),d.options.scheduler?d.options.scheduler(d):d()};s.forEach(c)}var Lo=bo("__proto__,__v_isRef,__isVue"),jn=new Set(Object.getOwnPropertyNames(Symbol).map(e=>Symbol[e]).filter(xt)),Ro=Bn(),Mo=Bn(!0),Ot=Do();function Do(){const e={};return["includes","indexOf","lastIndexOf"].forEach(t=>{e[t]=function(...n){const r=g(this);for(let i=0,a=this.length;i<a;i++)S(r,"get",i+"");const o=r[t](...n);return o===-1||o===!1?r[t](...n.map(g)):o}}),["push","pop","shift","unshift","splice"].forEach(t=>{e[t]=function(...n){To();const r=g(this)[t].apply(this,n);return Fn(),r}}),e}function Bn(e=!1,t=!1){return function(r,o,i){if(o==="__v_isReactive")return!e;if(o==="__v_isReadonly")return e;if(o==="__v_raw"&&i===(e?t?Jo:Vn:t?qo:Wn).get(r))return r;const a=U(r);if(!e&&a&&Oe(Ot,o))return Reflect.get(Ot,o,i);const s=Reflect.get(r,o,i);return(xt(o)?jn.has(o):Lo(o))||(e||S(r,"get",o),t)?s:Ze(s)?!a||!mt(o)?s.value:s:Te(s)?e?Hn(s):_t(s):s}}var No=Fo();function Fo(e=!1){return function(n,r,o,i){let a=n[r];if(!e&&(o=g(o),a=g(a),!U(n)&&Ze(a)&&!Ze(o)))return a.value=o,!0;const s=U(n)&&mt(r)?Number(r)<n.length:Oe(n,r),l=Reflect.set(n,r,o,i);return n===g(i)&&(s?Dn(o,a)&&M(n,"set",r,o,a):M(n,"add",r,o)),l}}function jo(e,t){const n=Oe(e,t),r=e[t],o=Reflect.deleteProperty(e,t);return o&&n&&M(e,"delete",t,void 0,r),o}function Bo(e,t){const n=Reflect.has(e,t);return(!xt(t)||!jn.has(t))&&S(e,"has",t),n}function $o(e){return S(e,"iterate",U(e)?"length":W),Reflect.ownKeys(e)}var Uo={get:Ro,set:No,deleteProperty:jo,has:Bo,ownKeys:$o},Wo={get:Mo,set(e,t){return console.warn(`Set operation on key "${String(t)}" failed: target is readonly.`,e),!0},deleteProperty(e,t){return console.warn(`Delete operation on key "${String(t)}" failed: target is readonly.`,e),!0}},vt=e=>Te(e)?_t(e):e,wt=e=>Te(e)?Hn(e):e,yt=e=>e,Ie=e=>Reflect.getPrototypeOf(e);function ue(e,t,n=!1,r=!1){e=e.__v_raw;const o=g(e),i=g(t);t!==i&&!n&&S(o,"get",t),!n&&S(o,"get",i);const{has:a}=Ie(o),s=r?yt:n?wt:vt;if(a.call(o,t))return s(e.get(t));if(a.call(o,i))return s(e.get(i));e!==o&&e.get(t)}function pe(e,t=!1){const n=this.__v_raw,r=g(n),o=g(e);return e!==o&&!t&&S(r,"has",e),!t&&S(r,"has",o),e===o?n.has(e):n.has(e)||n.has(o)}function fe(e,t=!1){return e=e.__v_raw,!t&&S(g(e),"iterate",W),Reflect.get(e,"size",e)}function Tt(e){e=g(e);const t=g(this);return Ie(t).has.call(t,e)||(t.add(e),M(t,"add",e,e)),this}function It(e,t){t=g(t);const n=g(this),{has:r,get:o}=Ie(n);let i=r.call(n,e);i?Un(n,r,e):(e=g(e),i=r.call(n,e));const a=o.call(n,e);return n.set(e,t),i?Dn(t,a)&&M(n,"set",e,t,a):M(n,"add",e,t),this}function Lt(e){const t=g(this),{has:n,get:r}=Ie(t);let o=n.call(t,e);o?Un(t,n,e):(e=g(e),o=n.call(t,e));const i=r?r.call(t,e):void 0,a=t.delete(e);return o&&M(t,"delete",e,void 0,i),a}function Rt(){const e=g(this),t=e.size!==0,n=ie(e)?new Map(e):new Set(e),r=e.clear();return t&&M(e,"clear",void 0,void 0,n),r}function ge(e,t){return function(r,o){const i=this,a=i.__v_raw,s=g(a),l=t?yt:e?wt:vt;return!e&&S(s,"iterate",W),a.forEach((c,d)=>r.call(o,l(c),l(d),i))}}function he(e,t,n){return function(...r){const o=this.__v_raw,i=g(o),a=ie(i),s=e==="entries"||e===Symbol.iterator&&a,l=e==="keys"&&a,c=o[e](...r),d=n?yt:t?wt:vt;return!t&&S(i,"iterate",l?Ye:W),{next(){const{value:p,done:f}=c.next();return f?{value:p,done:f}:{value:s?[d(p[0]),d(p[1])]:d(p),done:f}},[Symbol.iterator](){return this}}}}function L(e){return function(...t){{const n=t[0]?`on key "${t[0]}" `:"";console.warn(`${So(e)} operation ${n}failed: target is readonly.`,g(this))}return e==="delete"?!1:this}}function Vo(){const e={get(i){return ue(this,i)},get size(){return fe(this)},has:pe,add:Tt,set:It,delete:Lt,clear:Rt,forEach:ge(!1,!1)},t={get(i){return ue(this,i,!1,!0)},get size(){return fe(this)},has:pe,add:Tt,set:It,delete:Lt,clear:Rt,forEach:ge(!1,!0)},n={get(i){return ue(this,i,!0)},get size(){return fe(this,!0)},has(i){return pe.call(this,i,!0)},add:L("add"),set:L("set"),delete:L("delete"),clear:L("clear"),forEach:ge(!0,!1)},r={get(i){return ue(this,i,!0,!0)},get size(){return fe(this,!0)},has(i){return pe.call(this,i,!0)},add:L("add"),set:L("set"),delete:L("delete"),clear:L("clear"),forEach:ge(!0,!0)};return["keys","values","entries",Symbol.iterator].forEach(i=>{e[i]=he(i,!1,!1),n[i]=he(i,!0,!1),t[i]=he(i,!1,!0),r[i]=he(i,!0,!0)}),[e,n,t,r]}var[Ho,Ko,ia,aa]=Vo();function $n(e,t){const n=e?Ko:Ho;return(r,o,i)=>o==="__v_isReactive"?!e:o==="__v_isReadonly"?e:o==="__v_raw"?r:Reflect.get(Oe(n,o)&&o in r?n:r,o,i)}var zo={get:$n(!1)},Go={get:$n(!0)};function Un(e,t,n){const r=g(n);if(r!==n&&t.call(e,r)){const o=Mn(e);console.warn(`Reactive ${o} contains both the raw and reactive versions of the same object${o==="Map"?" as keys":""}, which can lead to inconsistencies. Avoid differentiating between the raw and reactive versions of an object and only use the reactive version if possible.`)}}var Wn=new WeakMap,qo=new WeakMap,Vn=new WeakMap,Jo=new WeakMap;function Qo(e){switch(e){case"Object":case"Array":return 1;case"Map":case"Set":case"WeakMap":case"WeakSet":return 2;default:return 0}}function Xo(e){return e.__v_skip||!Object.isExtensible(e)?0:Qo(Mn(e))}function _t(e){return e&&e.__v_isReadonly?e:Kn(e,!1,Uo,zo,Wn)}function Hn(e){return Kn(e,!0,Wo,Go,Vn)}function Kn(e,t,n,r,o){if(!Te(e))return console.warn(`value cannot be made reactive: ${String(e)}`),e;if(e.__v_raw&&!(t&&e.__v_isReactive))return e;const i=o.get(e);if(i)return i;const a=Xo(e);if(a===0)return e;const s=new Proxy(e,a===2?r:n);return o.set(e,s),s}function g(e){return e&&g(e.__v_raw)||e}function Ze(e){return!!(e&&e.__v_isRef===!0)}C("nextTick",()=>ft);C("dispatch",e=>oe.bind(oe,e));C("watch",(e,{evaluateLater:t,cleanup:n})=>(r,o)=>{let i=t(r),s=Ut(()=>{let l;return i(c=>l=c),l},o);n(s)});C("store",po);C("data",e=>Jt(e));C("root",e=>Ee(e));C("refs",e=>(e._x_refs_proxy||(e._x_refs_proxy=le(Yo(e))),e._x_refs_proxy));function Yo(e){let t=[];return X(e,n=>{n._x_refs&&t.push(n._x_refs)}),t}var De={};function zn(e){return De[e]||(De[e]=0),++De[e]}function Zo(e,t){return X(e,n=>{if(n._x_ids&&n._x_ids[t])return!0})}function ei(e,t){e._x_ids||(e._x_ids={}),e._x_ids[t]||(e._x_ids[t]=zn(t))}C("id",(e,{cleanup:t})=>(n,r=null)=>{let o=`${n}${r?`-${r}`:""}`;return ti(e,o,t,()=>{let i=Zo(e,n),a=i?i._x_ids[n]:zn(n);return r?`${n}-${a}-${r}`:`${n}-${a}`})});Pe((e,t)=>{e._x_id&&(t._x_id=e._x_id)});function ti(e,t,n,r){if(e._x_id||(e._x_id={}),e._x_id[t])return e._x_id[t];let o=r();return e._x_id[t]=o,n(()=>{delete e._x_id[t]}),o}C("el",e=>e);Gn("Focus","focus","focus");Gn("Persist","persist","persist");function Gn(e,t,n){C(t,r=>k(`You can't use [$${t}] without first installing the "${e}" plugin here: https://alpinejs.dev/plugins/${n}`,r))}b("modelable",(e,{expression:t},{effect:n,evaluateLater:r,cleanup:o})=>{let i=r(t),a=()=>{let d;return i(p=>d=p),d},s=r(`${t} = __placeholder`),l=d=>s(()=>{},{scope:{__placeholder:d}}),c=a();l(c),queueMicrotask(()=>{if(!e._x_model)return;e._x_removeModelListeners.default();let d=e._x_model.get,p=e._x_model.set,f=On({get(){return d()},set(v){p(v)}},{get(){return a()},set(v){l(v)}});o(f)})});b("teleport",(e,{modifiers:t,expression:n},{cleanup:r})=>{e.tagName.toLowerCase()!=="template"&&k("x-teleport can only be used on a <template> tag",e);let o=Mt(n),i=e.content.cloneNode(!0).firstElementChild;e._x_teleport=i,i._x_teleportBack=e,e.setAttribute("data-teleport-template",!0),i.setAttribute("data-teleport-target",!0),e._x_forwardEvents&&e._x_forwardEvents.forEach(s=>{i.addEventListener(s,l=>{l.stopPropagation(),e.dispatchEvent(new l.constructor(l.type,l))})}),se(i,{},e);let a=(s,l,c)=>{c.includes("prepend")?l.parentNode.insertBefore(s,l):c.includes("append")?l.parentNode.insertBefore(s,l.nextSibling):l.appendChild(s)};x(()=>{a(i,o,t),D(()=>{T(i)})()}),e._x_teleportPutBack=()=>{let s=Mt(n);x(()=>{a(e._x_teleport,s,t)})},r(()=>x(()=>{i.remove(),Y(i)}))});var ni=document.createElement("div");function Mt(e){let t=D(()=>document.querySelector(e),()=>ni)();return t||k(`Cannot find x-teleport element for selector: "${e}"`),t}var qn=()=>{};qn.inline=(e,{modifiers:t},{cleanup:n})=>{t.includes("self")?e._x_ignoreSelf=!0:e._x_ignore=!0,n(()=>{t.includes("self")?delete e._x_ignoreSelf:delete e._x_ignore})};b("ignore",qn);b("effect",D((e,{expression:t},{effect:n})=>{n(y(e,t))}));function et(e,t,n,r){let o=e,i=l=>r(l),a={},s=(l,c)=>d=>c(l,d);if(n.includes("dot")&&(t=ri(t)),n.includes("camel")&&(t=oi(t)),n.includes("passive")&&(a.passive=!0),n.includes("capture")&&(a.capture=!0),n.includes("window")&&(o=window),n.includes("document")&&(o=document),n.includes("debounce")){let l=n[n.indexOf("debounce")+1]||"invalid-wait",c=ye(l.split("ms")[0])?Number(l.split("ms")[0]):250;i=An(i,c)}if(n.includes("throttle")){let l=n[n.indexOf("throttle")+1]||"invalid-wait",c=ye(l.split("ms")[0])?Number(l.split("ms")[0]):250;i=Pn(i,c)}return n.includes("prevent")&&(i=s(i,(l,c)=>{c.preventDefault(),l(c)})),n.includes("stop")&&(i=s(i,(l,c)=>{c.stopPropagation(),l(c)})),n.includes("once")&&(i=s(i,(l,c)=>{l(c),o.removeEventListener(t,i,a)})),(n.includes("away")||n.includes("outside"))&&(o=document,i=s(i,(l,c)=>{e.contains(c.target)||c.target.isConnected!==!1&&(e.offsetWidth<1&&e.offsetHeight<1||e._x_isShown!==!1&&l(c))})),n.includes("self")&&(i=s(i,(l,c)=>{c.target===e&&l(c)})),(ai(t)||Jn(t))&&(i=s(i,(l,c)=>{si(c,n)||l(c)})),o.addEventListener(t,i,a),()=>{o.removeEventListener(t,i,a)}}function ri(e){return e.replace(/-/g,".")}function oi(e){return e.toLowerCase().replace(/-(\w)/g,(t,n)=>n.toUpperCase())}function ye(e){return!Array.isArray(e)&&!isNaN(e)}function ii(e){return[" ","_"].includes(e)?e:e.replace(/([a-z])([A-Z])/g,"$1-$2").replace(/[_\s]/,"-").toLowerCase()}function ai(e){return["keydown","keyup"].includes(e)}function Jn(e){return["contextmenu","click","mouse"].some(t=>e.includes(t))}function si(e,t){let n=t.filter(i=>!["window","document","prevent","stop","once","capture","self","away","outside","passive"].includes(i));if(n.includes("debounce")){let i=n.indexOf("debounce");n.splice(i,ye((n[i+1]||"invalid-wait").split("ms")[0])?2:1)}if(n.includes("throttle")){let i=n.indexOf("throttle");n.splice(i,ye((n[i+1]||"invalid-wait").split("ms")[0])?2:1)}if(n.length===0||n.length===1&&Dt(e.key).includes(n[0]))return!1;const o=["ctrl","shift","alt","meta","cmd","super"].filter(i=>n.includes(i));return n=n.filter(i=>!o.includes(i)),!(o.length>0&&o.filter(a=>((a==="cmd"||a==="super")&&(a="meta"),e[`${a}Key`])).length===o.length&&(Jn(e.type)||Dt(e.key).includes(n[0])))}function Dt(e){if(!e)return[];e=ii(e);let t={ctrl:"control",slash:"/",space:" ",spacebar:" ",cmd:"meta",esc:"escape",up:"arrow-up",down:"arrow-down",left:"arrow-left",right:"arrow-right",period:".",comma:",",equal:"=",minus:"-",underscore:"_"};return t[e]=e,Object.keys(t).map(n=>{if(t[n]===e)return n}).filter(n=>n)}b("model",(e,{modifiers:t,expression:n},{effect:r,cleanup:o})=>{let i=e;t.includes("parent")&&(i=e.parentNode);let a=y(i,n),s;typeof n=="string"?s=y(i,`${n} = __placeholder`):typeof n=="function"&&typeof n()=="string"?s=y(i,`${n()} = __placeholder`):s=()=>{};let l=()=>{let f;return a(v=>f=v),Nt(f)?f.get():f},c=f=>{let v;a(I=>v=I),Nt(v)?v.set(f):s(()=>{},{scope:{__placeholder:f}})};typeof n=="string"&&e.type==="radio"&&x(()=>{e.hasAttribute("name")||e.setAttribute("name",n)});var d=e.tagName.toLowerCase()==="select"||["checkbox","radio"].includes(e.type)||t.includes("lazy")?"change":"input";let p=R?()=>{}:et(e,d,t,f=>{c(Ne(e,t,f,l()))});if(t.includes("fill")&&([void 0,null,""].includes(l())||ht(e)&&Array.isArray(l())||e.tagName.toLowerCase()==="select"&&e.multiple)&&c(Ne(e,t,{target:e},l())),e._x_removeModelListeners||(e._x_removeModelListeners={}),e._x_removeModelListeners.default=p,o(()=>e._x_removeModelListeners.default()),e.form){let f=et(e.form,"reset",[],v=>{ft(()=>e._x_model&&e._x_model.set(Ne(e,t,{target:e},l())))});o(()=>f())}e._x_model={get(){return l()},set(f){c(f)}},e._x_forceModelUpdate=f=>{f===void 0&&typeof n=="string"&&n.match(/\./)&&(f=""),window.fromModel=!0,x(()=>_n(e,"value",f)),delete window.fromModel},r(()=>{let f=l();t.includes("unintrusive")&&document.activeElement.isSameNode(e)||e._x_forceModelUpdate(f)})});function Ne(e,t,n,r){return x(()=>{if(n instanceof CustomEvent&&n.detail!==void 0)return n.detail!==null&&n.detail!==void 0?n.detail:n.target.value;if(ht(e))if(Array.isArray(r)){let o=null;return t.includes("number")?o=Fe(n.target.value):t.includes("boolean")?o=me(n.target.value):o=n.target.value,n.target.checked?r.includes(o)?r:r.concat([o]):r.filter(i=>!li(i,o))}else return n.target.checked;else{if(e.tagName.toLowerCase()==="select"&&e.multiple)return t.includes("number")?Array.from(n.target.selectedOptions).map(o=>{let i=o.value||o.text;return Fe(i)}):t.includes("boolean")?Array.from(n.target.selectedOptions).map(o=>{let i=o.value||o.text;return me(i)}):Array.from(n.target.selectedOptions).map(o=>o.value||o.text);{let o;return En(e)?n.target.checked?o=n.target.value:o=r:o=n.target.value,t.includes("number")?Fe(o):t.includes("boolean")?me(o):t.includes("trim")?o.trim():o}}})}function Fe(e){let t=e?parseFloat(e):null;return ci(t)?t:e}function li(e,t){return e==t}function ci(e){return!Array.isArray(e)&&!isNaN(e)}function Nt(e){return e!==null&&typeof e=="object"&&typeof e.get=="function"&&typeof e.set=="function"}b("cloak",e=>queueMicrotask(()=>x(()=>e.removeAttribute(Q("cloak")))));xn(()=>`[${Q("init")}]`);b("init",D((e,{expression:t},{evaluate:n})=>typeof t=="string"?!!t.trim()&&n(t,{},!1):n(t,{},!1)));b("text",(e,{expression:t},{effect:n,evaluateLater:r})=>{let o=r(t);n(()=>{o(i=>{x(()=>{e.textContent=i})})})});b("html",(e,{expression:t},{effect:n,evaluateLater:r})=>{let o=r(t);n(()=>{o(i=>{x(()=>{e.innerHTML=i,e._x_ignoreSelf=!0,T(e),delete e._x_ignoreSelf})})})});dt(an(":",sn(Q("bind:"))));var Qn=(e,{value:t,modifiers:n,expression:r,original:o},{effect:i,cleanup:a})=>{if(!t){let l={};go(l),y(e,r)(d=>{In(e,d,o)},{scope:l});return}if(t==="key")return di(e,r);if(e._x_inlineBindings&&e._x_inlineBindings[t]&&e._x_inlineBindings[t].extract)return;let s=y(e,r);i(()=>s(l=>{l===void 0&&typeof r=="string"&&r.match(/\./)&&(l=""),x(()=>_n(e,t,l,n))})),a(()=>{e._x_undoAddedClasses&&e._x_undoAddedClasses(),e._x_undoAddedStyles&&e._x_undoAddedStyles()})};Qn.inline=(e,{value:t,modifiers:n,expression:r})=>{t&&(e._x_inlineBindings||(e._x_inlineBindings={}),e._x_inlineBindings[t]={expression:r,extract:!1})};b("bind",Qn);function di(e,t){e._x_keyExpression=t}hn(()=>`[${Q("data")}]`);b("data",(e,{expression:t},{cleanup:n})=>{if(ui(e))return;t=t===""?"{}":t;let r={};Ve(r,e);let o={};xo(o,r);let i=$(e,t,{scope:o});(i===void 0||i===!0)&&(i={}),Ve(i,e);let a=q(i);Qt(a);let s=se(e,a);a.init&&$(e,a.init),n(()=>{a.destroy&&$(e,a.destroy),s()})});Pe((e,t)=>{e._x_dataStack&&(t._x_dataStack=e._x_dataStack,t.setAttribute("data-has-alpine-state",!0))});function ui(e){return R?Qe?!0:e.hasAttribute("data-has-alpine-state"):!1}b("show",(e,{modifiers:t,expression:n},{effect:r})=>{let o=y(e,n);e._x_doHide||(e._x_doHide=()=>{x(()=>{e.style.setProperty("display","none",t.includes("important")?"important":void 0)})}),e._x_doShow||(e._x_doShow=()=>{x(()=>{e.style.length===1&&e.style.display==="none"?e.removeAttribute("style"):e.style.removeProperty("display")})});let i=()=>{e._x_doHide(),e._x_isShown=!1},a=()=>{e._x_doShow(),e._x_isShown=!0},s=()=>setTimeout(a),l=qe(p=>p?a():i(),p=>{typeof e._x_toggleAndCascadeWithTransitions=="function"?e._x_toggleAndCascadeWithTransitions(e,p,a,i):p?s():i()}),c,d=!0;r(()=>o(p=>{!d&&p===c||(t.includes("immediate")&&(p?s():i()),l(p),c=p,d=!1)}))});b("for",(e,{expression:t},{effect:n,cleanup:r})=>{let o=fi(t),i=y(e,o.items),a=y(e,e._x_keyExpression||"index");e._x_prevKeys=[],e._x_lookup={},n(()=>pi(e,o,i,a)),r(()=>{Object.values(e._x_lookup).forEach(s=>x(()=>{Y(s),s.remove()})),delete e._x_prevKeys,delete e._x_lookup})});function pi(e,t,n,r){let o=a=>typeof a=="object"&&!Array.isArray(a),i=e;n(a=>{gi(a)&&a>=0&&(a=Array.from(Array(a).keys(),u=>u+1)),a===void 0&&(a=[]);let s=e._x_lookup,l=e._x_prevKeys,c=[],d=[];if(o(a))a=Object.entries(a).map(([u,h])=>{let m=Ft(t,h,u,a);r(w=>{d.includes(w)&&k("Duplicate key on x-for",e),d.push(w)},{scope:{index:u,...m}}),c.push(m)});else for(let u=0;u<a.length;u++){let h=Ft(t,a[u],u,a);r(m=>{d.includes(m)&&k("Duplicate key on x-for",e),d.push(m)},{scope:{index:u,...h}}),c.push(h)}let p=[],f=[],v=[],I=[];for(let u=0;u<l.length;u++){let h=l[u];d.indexOf(h)===-1&&v.push(h)}l=l.filter(u=>!v.includes(u));let de="template";for(let u=0;u<d.length;u++){let h=d[u],m=l.indexOf(h);if(m===-1)l.splice(u,0,h),p.push([de,u]);else if(m!==u){let w=l.splice(u,1)[0],_=l.splice(m-1,1)[0];l.splice(u,0,_),l.splice(m,0,w),f.push([w,_])}else I.push(h);de=h}for(let u=0;u<v.length;u++){let h=v[u];h in s&&(x(()=>{Y(s[h]),s[h].remove()}),delete s[h])}for(let u=0;u<f.length;u++){let[h,m]=f[u],w=s[h],_=s[m],K=document.createElement("div");x(()=>{_||k('x-for ":key" is undefined or invalid',i,m,s),_.after(K),w.after(_),_._x_currentIfEl&&_.after(_._x_currentIfEl),K.before(w),w._x_currentIfEl&&w.after(w._x_currentIfEl),K.remove()}),_._x_refreshXForScope(c[d.indexOf(m)])}for(let u=0;u<p.length;u++){let[h,m]=p[u],w=h==="template"?i:s[h];w._x_currentIfEl&&(w=w._x_currentIfEl);let _=c[m],K=d[m],Z=document.importNode(i.content,!0).firstElementChild,kt=q(_);se(Z,kt,i),Z._x_refreshXForScope=rr=>{Object.entries(rr).forEach(([or,ir])=>{kt[or]=ir})},x(()=>{w.after(Z),D(()=>T(Z))()}),typeof K=="object"&&k("x-for key cannot be an object, it must be a string or an integer",i),s[K]=Z}for(let u=0;u<I.length;u++)s[I[u]]._x_refreshXForScope(c[d.indexOf(I[u])]);i._x_prevKeys=d})}function fi(e){let t=/,([^,\}\]]*)(?:,([^,\}\]]*))?$/,n=/^\s*\(|\)\s*$/g,r=/([\s\S]*?)\s+(?:in|of)\s+([\s\S]*)/,o=e.match(r);if(!o)return;let i={};i.items=o[2].trim();let a=o[1].replace(n,"").trim(),s=a.match(t);return s?(i.item=a.replace(t,"").trim(),i.index=s[1].trim(),s[2]&&(i.collection=s[2].trim())):i.item=a,i}function Ft(e,t,n,r){let o={};return/^\[.*\]$/.test(e.item)&&Array.isArray(t)?e.item.replace("[","").replace("]","").split(",").map(a=>a.trim()).forEach((a,s)=>{o[a]=t[s]}):/^\{.*\}$/.test(e.item)&&!Array.isArray(t)&&typeof t=="object"?e.item.replace("{","").replace("}","").split(",").map(a=>a.trim()).forEach(a=>{o[a]=t[a]}):o[e.item]=t,e.index&&(o[e.index]=n),e.collection&&(o[e.collection]=r),o}function gi(e){return!Array.isArray(e)&&!isNaN(e)}function Xn(){}Xn.inline=(e,{expression:t},{cleanup:n})=>{let r=Ee(e);r._x_refs||(r._x_refs={}),r._x_refs[t]=e,n(()=>delete r._x_refs[t])};b("ref",Xn);b("if",(e,{expression:t},{effect:n,cleanup:r})=>{e.tagName.toLowerCase()!=="template"&&k("x-if can only be used on a <template> tag",e);let o=y(e,t),i=()=>{if(e._x_currentIfEl)return e._x_currentIfEl;let s=e.content.cloneNode(!0).firstElementChild;return se(s,{},e),x(()=>{e.after(s),D(()=>T(s))()}),e._x_currentIfEl=s,e._x_undoIf=()=>{x(()=>{Y(s),s.remove()}),delete e._x_currentIfEl},s},a=()=>{e._x_undoIf&&(e._x_undoIf(),delete e._x_undoIf)};n(()=>o(s=>{s?i():a()})),r(()=>e._x_undoIf&&e._x_undoIf())});b("id",(e,{expression:t},{evaluate:n})=>{n(t).forEach(o=>ei(e,o))});Pe((e,t)=>{e._x_ids&&(t._x_ids=e._x_ids)});dt(an("@",sn(Q("on:"))));b("on",D((e,{value:t,modifiers:n,expression:r},{cleanup:o})=>{let i=r?y(e,r):()=>{};e.tagName.toLowerCase()==="template"&&(e._x_forwardEvents||(e._x_forwardEvents=[]),e._x_forwardEvents.includes(t)||e._x_forwardEvents.push(t));let a=et(e,t,n,s=>{i(()=>{},{scope:{$event:s},params:[s]})});o(()=>a())}));Le("Collapse","collapse","collapse");Le("Intersect","intersect","intersect");Le("Focus","trap","focus");Le("Mask","mask","mask");function Le(e,t,n){b(t,r=>k(`You can't use [x-${t}] without first installing the "${e}" plugin here: https://alpinejs.dev/plugins/${n}`,r))}ce.setEvaluator(tn);ce.setReactivityEngine({reactive:_t,effect:Eo,release:Ao,raw:g});var hi=ce,Yn=hi;const xi={async loginApi(e,t){const n=await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:e,password:t})}),r=await n.json().catch(()=>({}));if(!n.ok){const o=new Error(r.code||"LOGIN_FAILED");throw o.code=r.code,o}return r}},_e={appContext:null,username:"",password:"",isLoading:!1,error:null,response:null,isLoggedIn:!1,token:null,init(e){this.appContext=e,this.isLoggedIn=!!localStorage.getItem("token"),this.token=localStorage.getItem("token")},async login(){if(this.isLoading=!0,this.error=null,!this.username||!this.username.trim()){this.error=this.appContext.t("errors.USERNAME_REQUIRED"),this.isLoading=!1;return}if(!this.password||!this.password.trim()){this.error=this.appContext.t("errors.PASSWORD_REQUIRED"),this.isLoading=!1;return}try{const e=await xi.loginApi(this.username,this.password);e.token?(this.token=e.token,localStorage.setItem("token",e.token),this.isLoggedIn=!0,window.location.href="/"):this.error=this.appContext.tError(e.code||"LOGIN_FAILED")}catch(e){console.error("Login error:",e),this.error=this.appContext.tError(e.code||"LOGIN_FAILED")}finally{this.isLoading=!1}}},mi=localStorage.getItem("darkMode")==="true";mi?document.documentElement.classList.add("dark"):document.documentElement.classList.remove("dark");const Zn={sidebarOpen:!1,darkMode:!1,init(){typeof window<"u"&&window.innerWidth>=1024&&(this.sidebarOpen=!0),this.darkMode=localStorage.getItem("darkMode")==="true",this.applyTheme(),localStorage.getItem("darkMode")===null&&(this.darkMode=window.matchMedia("(prefers-color-scheme: dark)").matches,localStorage.setItem("darkMode",this.darkMode),this.applyTheme()),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",e=>{localStorage.getItem("darkMode")===null&&(this.darkMode=e.matches,localStorage.setItem("darkMode",this.darkMode),this.applyTheme())})},toggleDarkMode(){this.darkMode=!this.darkMode,localStorage.setItem("darkMode",this.darkMode),this.applyTheme()},applyTheme(){this.darkMode?document.documentElement.classList.add("dark"):document.documentElement.classList.remove("dark")}},tt={cloneCommand:"git clone https://github.com/you/vanilla-webapp-framework.git",copyFeedback:"",carouselCurrent:0,carouselDots:[0,1,2,3],carouselTimer:null,init(){this.copyFeedback=""},initCarousel(){this.stopCarousel(),this.carouselCurrent=0,this.carouselTimer=setInterval(()=>{this.goSlide(this.carouselCurrent+1)},5e3)},stopCarousel(){this.carouselTimer&&(clearInterval(this.carouselTimer),this.carouselTimer=null)},goSlide(e){const t=this.carouselDots.length;this.carouselCurrent=(e%t+t)%t},prevSlide(){this.goSlide(this.carouselCurrent-1),this.restartCarousel()},nextSlide(){this.goSlide(this.carouselCurrent+1),this.restartCarousel()},restartCarousel(){this.stopCarousel(),this.carouselTimer=setInterval(()=>{this.goSlide(this.carouselCurrent+1)},5e3)},async copyCloneCommand(){var t,n,r;const e=((n=(t=window.spaApp)==null?void 0:t.t)==null?void 0:n.bind(window.spaApp))??(o=>o);try{(r=navigator.clipboard)!=null&&r.writeText?(await navigator.clipboard.writeText(this.cloneCommand),this.copyFeedback=e("welcome.copied")):this.copyFeedback=e("welcome.copyUnavailable")}catch{this.copyFeedback=e("welcome.copyFailed")}setTimeout(()=>{this.copyFeedback=""},2e3)}},bi={appContext:null,isLoading:!1,error:null,response:null,token:null,init(e){this.appContext=e,this.isLoading=!1,this.error=null,this.response=null,this.token=localStorage.getItem("token")},async fetchProtectedData(){var e,t;if(!this.appContext||!this.token){this.error=((e=this.appContext)==null?void 0:e.t("errors.NOT_LOGGED_IN"))??"Not logged in",(t=this.appContext)==null||t.logout();return}this.isLoading=!0,this.error=null;try{const n=await fetch("/api/data",{headers:{Authorization:`Bearer ${this.token}`}});n.ok?this.response=await n.json():(n.status===401?(this.error=this.appContext.t("errors.UNAUTHORIZED"),this.appContext.logout()):this.error=this.appContext.t("errors.HTTP_ERROR",{status:n.status}),this.response=null)}catch{this.error=this.appContext.t("errors.FETCH_FAILED"),this.appContext.logout()}finally{this.isLoading=!1}},async fetchPublicData(){this.isLoading=!0,this.error=null;try{const e=await fetch("/api/public");e.ok?this.response=await e.json():(this.error=this.appContext.t("errors.HTTP_ERROR",{status:e.status}),this.response=null)}catch{this.error=this.appContext.t("errors.FETCH_FAILED")}finally{this.isLoading=!1}}},vi={abc:0,isLoading:!1,appContext:null,init(e){this.appContext=e,console.log("Test page controller initialized"),this.isLoading=!1},async ttt(){this.isLoading=!0,console.log("ttt called, abc is:",this.abc),await new Promise(e=>setTimeout(e,500)),console.log("ttt finished"),this.isLoading=!1}},wi={async registerApi(e,t){const n=await fetch("/api/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:e,password:t})}),r=await n.json().catch(()=>({}));if(!n.ok){const o=new Error(r.code||"REGISTRATION_FAILED");throw o.code=r.code,o}return r}},yi={appContext:null,username:"",password:"",confirmPassword:"",isLoading:!1,error:null,success:null,init(e){this.appContext=e,this.username="",this.password="",this.confirmPassword="",this.isLoading=!1,this.error=null,this.success=null},async register(){if(this.isLoading=!0,this.error=null,this.success=null,!this.username||!this.username.trim()){this.error=this.appContext.t("errors.USERNAME_REQUIRED"),this.isLoading=!1;return}if(!this.password||this.password.length<6){this.error=this.appContext.t("errors.PASSWORD_TOO_SHORT"),this.isLoading=!1;return}if(this.password!==this.confirmPassword){this.error=this.appContext.t("errors.PASSWORDS_DO_NOT_MATCH"),this.isLoading=!1;return}try{const e=await wi.registerApi(this.username,this.password);e.code==="USER_CREATED"?(this.success=this.appContext.t("register.success"),this.username="",this.password="",this.confirmPassword="",setTimeout(()=>{this.appContext.loadPage("login-register-container","login")},2e3)):this.error=this.appContext.tError(e.code||"REGISTRATION_FAILED")}catch(e){console.error("Registration failed:",e),this.error=this.appContext.tError(e.code||"REGISTRATION_FAILED")}finally{this.isLoading=!1}}},_i=`<!-- Sidebar Navigation -->
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
        <span class="text-xl font-bold text-gray-800 dark:text-white ml-2 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.appName')"></span>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.dashboard')"></span>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.analytics')"></span>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.settings')"></span>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.profile')"></span>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="t('menu.logout')"></span>
        </button>
      </nav>

      <!-- Language + Dark Mode -->
      <div class="p-2 border-t border-gray-200 dark:border-gray-700 space-y-1">
        <div class="px-4 py-2 flex items-center justify-center group-hover:justify-start">
          <div class="flex items-center gap-1 text-sm" role="group" :aria-label="t('common.language')">
            <button type="button" @click="setLocale('en')"
                    :class="locale === 'en' ? 'font-semibold text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'"
                    :aria-pressed="locale === 'en'">EN</button>
            <span class="text-gray-300 dark:text-gray-600" aria-hidden="true">|</span>
            <button type="button" @click="setLocale('pt-BR')"
                    :class="locale === 'pt-BR' ? 'font-semibold text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'"
                    :aria-pressed="locale === 'pt-BR'">PT</button>
          </div>
        </div>
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
          <span class="ml-3 hidden group-hover:inline-block whitespace-nowrap" x-text="menuController.darkMode ? t('common.lightMode') : t('common.darkMode')"></span>
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
`,ki=`<!-- Login Form Partial -->

<div x-show="!isLoggedIn" class="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6" >
    <div class="space-y-4">
        <div class="text-center">
            <a href="#" @click.prevent="showWelcomePage()"
               class="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
               x-text="t('login.backToWelcome')">
            </a>
        </div>
        <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white" x-text="t('login.title')"></h1>
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="t('login.username')"></label>
            <input type="text" 
                    x-model="loginController.username" 
                    class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                    :disabled="loginController.isLoading">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="t('login.password')"></label>
            <input type="password" 
                    x-model="loginController.password" 
                    class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                    :disabled="loginController.isLoading">
        </div>
        <button @click="loginController.login()" 
                class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors duration-200 disabled:opacity-50"
                :disabled="loginController.isLoading">
            <span x-show="!loginController.isLoading" x-text="t('common.login')"></span>
            <span x-show="loginController.isLoading" x-text="t('common.loading')"></span>
        </button>

        <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400" x-text="t('common.orContinueWith')"></span>
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
           class="text-xs text-center text-gray-500 dark:text-gray-400"
           x-text="t('login.oauthHint')">
        </p>

        <div class="text-center mt-4">
            <a href="#" @click.prevent="loadPage('login-register-container', 'user_registry');" 
                class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
                x-text="t('login.noAccount')">
            </a>
        </div>
        
        <div x-show="loginController.error" 
            class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
            x-text="loginController.error">
        </div>
        
        <div x-show="loginController.response" class="mt-4">
            <h2 class="text-lg font-semibold mb-2 text-gray-800 dark:text-white" x-text="t('common.response')"></h2>
            <pre class="bg-gray-100 dark:bg-gray-700 p-4 rounded-md overflow-x-auto text-gray-800 dark:text-gray-200" x-text="JSON.stringify(loginController.response, null, 2)"></pre>
        </div>
    </div>
</div>
`,Si=`<!-- User Registration Page -->

<div class="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="space-y-4">
        <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white" x-text="t('register.title')"></h1>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="t('register.username')"></label>
            <input 
                type="text" 
                x-model="currentPage.username" 
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                :disabled="currentPage.isLoading">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="t('register.password')"></label>
            <input 
                type="password" 
                x-model="currentPage.password" 
                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:ring-indigo-400"
                :disabled="currentPage.isLoading">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300" x-text="t('register.confirmPassword')"></label>
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
            <span x-show="!currentPage.isLoading" x-text="t('common.register')"></span>
            <span x-show="currentPage.isLoading" x-text="t('common.processing')"></span>
        </button>
        
        <div class="text-center mt-4">
            <a href="#" @click.prevent="loadPage('login-register-container', 'login');" 
                class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
                x-text="t('register.hasAccount')">
            </a>
        </div>
        
        <div 
            x-show="currentPage.error" 
            class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
            x-text="currentPage.error">
        </div>
        
        <div 
            x-show="currentPage.success" 
            class="mt-4 p-4 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md" 
            x-text="currentPage.success">
        </div>
    </div>
</div>
`,Ci=`<!-- Public welcome page — loaded into #public-container -->
<div class="bg-gray-50 text-gray-900 antialiased dark:bg-gray-950 dark:text-gray-100 min-h-screen">

    <header class="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm" aria-hidden="true">V</div>
                <span class="font-semibold text-gray-900 dark:text-white">Vanilla WebApp</span>
            </div>
            <nav class="hidden sm:flex items-center gap-6 text-sm text-gray-600 dark:text-gray-300" aria-label="Welcome page sections">
                <a href="#carousel" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition" x-text="t('welcome.navSeeItWork')"></a>
                <a href="#features" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition" x-text="t('welcome.navFeatures')"></a>
                <a href="#partners" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition" x-text="t('welcome.navPartners')"></a>
            </nav>
            <div class="flex items-center gap-3">
                <button type="button"
                        @click="menuController.toggleDarkMode()"
                        :aria-label="t('common.toggleDarkMode')"
                        class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition">
                    <svg x-show="menuController.darkMode" x-cloak class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.36 6.36l-.71-.71M6.34 6.34l-.71-.71m12.02 0l-.71.71M6.34 17.66l-.71.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                    <svg x-show="!menuController.darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
                </button>
                <div class="flex items-center gap-1 text-sm" role="group" :aria-label="t('common.language')">
                    <button type="button" @click="setLocale('en')"
                            :class="locale === 'en' ? 'font-semibold text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'"
                            :aria-pressed="locale === 'en'">EN</button>
                    <span class="text-gray-300 dark:text-gray-600" aria-hidden="true">|</span>
                    <button type="button" @click="setLocale('pt-BR')"
                            :class="locale === 'pt-BR' ? 'font-semibold text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'"
                            :aria-pressed="locale === 'pt-BR'">PT</button>
                </div>
                <button type="button"
                        @click="showLoginPage()"
                        class="inline-flex items-center gap-2 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                    <span x-text="t('welcome.signIn')"></span>
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
                <span x-text="t('welcome.badge')"></span>
            </p>
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight max-w-3xl mx-auto leading-tight" x-text="t('welcome.heroTitle')"></h1>
            <p class="mt-4 text-base sm:text-lg text-indigo-100 max-w-2xl mx-auto" x-text="t('welcome.heroSubtitle')"></p>
            <div class="mt-7 inline-flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 max-w-full px-2">
                <code class="flex items-center text-left text-xs sm:text-sm bg-indigo-950/40 text-emerald-300 px-4 py-2.5 rounded-lg border border-white/20 font-mono overflow-x-auto">
                    <span class="text-indigo-300/70 mr-2 select-none">$</span><span x-text="welcomeController.cloneCommand"></span>
                </code>
                <button type="button"
                        @click="welcomeController.copyCloneCommand()"
                        class="shrink-0 inline-flex items-center justify-center gap-2 bg-white text-indigo-700 font-semibold px-6 py-2.5 rounded-lg hover:bg-indigo-50 transition shadow-lg text-sm">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                    <span x-text="welcomeController.copyFeedback || t('welcome.copyCommand')"></span>
                </button>
            </div>
            <div class="mt-7 flex flex-wrap justify-center gap-x-6 gap-y-1 text-xs sm:text-sm text-indigo-200">
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span x-text="t('welcome.trustAuth')"></span></span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span x-text="t('welcome.trustVite')"></span></span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span x-text="t('welcome.trustAlembic')"></span></span>
                <span class="inline-flex items-center gap-1.5"><svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span x-text="t('welcome.trustDocker')"></span></span>
            </div>
        </div>
    </section>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12 lg:py-16">
        <div class="lg:grid lg:grid-cols-[1fr_300px] lg:gap-10 items-start">

            <main class="min-w-0 space-y-14">
                <section id="carousel">
                    <div class="mb-6 lg:text-left text-center">
                        <p class="text-xs uppercase tracking-widest text-indigo-600 dark:text-indigo-400 font-semibold" x-text="t('welcome.navSeeItWork')"></p>
                        <h2 class="mt-1 text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white" x-text="t('welcome.carouselTitle')"></h2>
                        <p class="mt-2 text-gray-600 dark:text-gray-400" x-text="t('welcome.carouselSubtitle')"></p>
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
                                            <span class="text-xs uppercase tracking-widest text-indigo-200" x-text="t('welcome.slide1Tag')"></span>
                                            <p class="mt-1 text-xl sm:text-2xl font-bold leading-snug" x-text="t('welcome.slide1Title')"></p>
                                            <p class="mt-2 text-sm text-indigo-100" x-text="t('welcome.slide1Desc')"></p>
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
                                            <div class="h-9 rounded-md bg-indigo-600 flex items-center justify-center text-white text-xs font-semibold" x-text="t('welcome.slide2SignIn')"></div>
                                            <div class="flex items-center gap-2 text-[10px] text-slate-500"><span class="flex-1 h-px bg-slate-700"></span><span x-text="t('welcome.slide2Or')"></span><span class="flex-1 h-px bg-slate-700"></span></div>
                                            <div class="h-9 rounded-md bg-white flex items-center justify-center text-slate-700 text-xs font-medium gap-2"><span class="w-3.5 h-3.5 rounded-full bg-gradient-to-br from-blue-500 to-red-500" aria-hidden="true"></span><span x-text="t('welcome.slide2Google')"></span></div>
                                            <div class="h-9 rounded-md bg-[#1877F2] flex items-center justify-center text-white text-xs font-medium" x-text="t('welcome.slide2Facebook')"></div>
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
                                        <p class="pt-2 text-xs text-slate-500" x-text="t('welcome.slide3Swagger')"></p>
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
                            <button type="button" @click="welcomeController.prevSlide()" class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition" :aria-label="t('welcome.carouselPrev')">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                            </button>
                            <div class="flex gap-2">
                                <button type="button"
                                        @click="welcomeController.goSlide(0); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 0 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        :aria-label="t('welcome.carouselSlide1Label')"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(1); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 1 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        :aria-label="t('welcome.carouselSlide2Label')"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(2); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 2 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        :aria-label="t('welcome.carouselSlide3Label')"></button>
                                <button type="button"
                                        @click="welcomeController.goSlide(3); welcomeController.restartCarousel()"
                                        :class="welcomeController.carouselCurrent === 3 ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
                                        class="h-2 rounded-full transition-all"
                                        :aria-label="t('welcome.carouselSlide4Label')"></button>
                            </div>
                            <button type="button" @click="welcomeController.nextSlide()" class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition" :aria-label="t('welcome.carouselNext')">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                            </button>
                        </div>
                    </div>
                </section>

                <section id="features">
                    <div class="mb-8 lg:text-left text-center">
                        <p class="text-xs uppercase tracking-widest text-indigo-600 dark:text-indigo-400 font-semibold" x-text="t('welcome.featuresEyebrow')"></p>
                        <h2 class="mt-1 text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white" x-text="t('welcome.featuresTitle')"></h2>
                    </div>
                    <div class="grid sm:grid-cols-3 gap-6">
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white" x-text="t('welcome.featureBackendTitle')"></h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm" x-text="t('welcome.featureBackendDesc')"></p>
                        </article>
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8l-4 4 4 4m10-8l4 4-4 4M14 4l-4 16"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white" x-text="t('welcome.featureFrontendTitle')"></h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm" x-text="t('welcome.featureFrontendDesc')"></p>
                        </article>
                        <article class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center lg:text-left hover:shadow-md hover:-translate-y-0.5 transition">
                            <div class="w-11 h-11 rounded-xl bg-indigo-100 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 mx-auto lg:mx-0">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            </div>
                            <h3 class="font-semibold text-gray-900 dark:text-white" x-text="t('welcome.featureSeoTitle')"></h3>
                            <p class="mt-2 text-gray-600 dark:text-gray-400 text-sm" x-text="t('welcome.featureSeoDesc')"></p>
                        </article>
                    </div>
                </section>
            </main>

            <aside id="partners" class="mt-12 lg:mt-0 lg:sticky lg:top-20 space-y-5">
                <p class="hidden lg:block text-xs uppercase tracking-widest text-gray-400 dark:text-gray-500 font-semibold mb-6" x-text="t('welcome.partnersTitle')"></p>

                <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
                    <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
                        <h3 class="text-sm font-bold text-gray-900 dark:text-white" x-text="t('welcome.partnersRecommended')"></h3>
                        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5" x-text="t('welcome.partnersSubtitle')"></p>
                    </div>
                    <div class="divide-y divide-gray-100 dark:divide-gray-800">
                        <a href="https://www.digitalocean.com/" target="_blank" rel="noopener noreferrer sponsored" class="block p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition group border-l-2 border-l-transparent hover:border-l-amber-400">
                            <div class="flex gap-3">
                                <div class="w-11 h-11 rounded-lg bg-gradient-to-br from-blue-400 to-blue-700 shrink-0 flex items-center justify-center text-white text-xs font-bold" aria-hidden="true">DO</div>
                                <div class="min-w-0">
                                    <p class="text-[10px] font-semibold uppercase text-amber-600 tracking-wider" x-text="t('welcome.partnerHosting')"></p>
                                    <p class="font-semibold text-sm text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 leading-snug transition" x-text="t('welcome.partnerDoTitle')"></p>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5" x-text="t('welcome.partnerDoDesc')"></p>
                                </div>
                            </div>
                        </a>
                        <a href="https://www.namecheap.com/" target="_blank" rel="noopener noreferrer sponsored" class="block p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition group border-l-2 border-l-transparent hover:border-l-amber-400">
                            <div class="flex gap-3">
                                <div class="w-11 h-11 rounded-lg bg-gradient-to-br from-orange-400 to-red-600 shrink-0 flex items-center justify-center text-white text-xs font-bold" aria-hidden="true">NC</div>
                                <div class="min-w-0">
                                    <p class="text-[10px] font-semibold uppercase text-amber-600 tracking-wider" x-text="t('welcome.partnerDomain')"></p>
                                    <p class="font-semibold text-sm text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 leading-snug transition" x-text="t('welcome.partnerNcTitle')"></p>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5" x-text="t('welcome.partnerNcDesc')"></p>
                                </div>
                            </div>
                        </a>
                    </div>
                    <p class="px-4 py-2 text-[10px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-800/40 border-t border-gray-100 dark:border-gray-800" x-text="t('welcome.affiliateNotice')"></p>
                </div>

                <div class="bg-gray-50 dark:bg-gray-900/40 border border-dashed border-gray-300 dark:border-gray-700 rounded-2xl overflow-hidden" aria-label="Ad slot medium rectangle">
                    <div class="px-3 py-2 border-b border-dashed border-gray-300 dark:border-gray-700">
                        <span class="text-[10px] font-mono text-gray-400 uppercase tracking-wider" x-text="t('welcome.adSponsored')"></span>
                    </div>
                    <div class="flex flex-col items-center justify-center py-14 px-4">
                        <span class="text-xs font-mono text-gray-400 uppercase" x-text="t('welcome.adSlot')"></span>
                        <span class="text-sm text-gray-500 dark:text-gray-400 mt-1" x-text="t('welcome.adMediumRect')"></span>
                        <span class="text-xs text-gray-400 mt-0.5">300 × 250</span>
                    </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-900/40 border border-dashed border-gray-300 dark:border-gray-700 rounded-2xl overflow-hidden" aria-label="Ad slot display banner">
                    <div class="flex flex-col items-center justify-center py-8 px-4">
                        <span class="text-xs font-mono text-gray-400 uppercase" x-text="t('welcome.adSlot')"></span>
                        <span class="text-sm text-gray-500 dark:text-gray-400 mt-1" x-text="t('welcome.adDisplayBanner')"></span>
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
                    <p class="mt-2 text-sm text-gray-400" x-text="t('welcome.footerTagline')"></p>
                </div>
                <div class="flex items-center gap-4">
                    <a href="https://github.com/" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 text-sm text-gray-300 hover:text-white transition">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.26.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.085 1.84 1.237 1.84 1.237 1.07 1.835 2.807 1.305 3.492.998.108-.776.42-1.305.762-1.605-2.665-.303-5.467-1.332-5.467-5.93 0-1.31.467-2.38 1.235-3.22-.124-.303-.535-1.523.117-3.176 0 0 1.008-.322 3.3 1.23a11.5 11.5 0 016.003 0c2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.806 5.624-5.479 5.92.43.372.823 1.102.823 2.222 0 1.605-.015 2.9-.015 3.295 0 .32.216.694.825.576C20.565 21.795 24 17.297 24 12c0-6.63-5.37-12-12-12z"/></svg>
                        <span x-text="t('welcome.footerGithub')"></span>
                    </a>
                    <button type="button"
                            @click="welcomeController.copyCloneCommand()"
                            class="inline-flex items-center gap-2 bg-indigo-500 hover:bg-indigo-400 text-white font-medium px-5 py-2.5 rounded-lg transition text-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        <span x-text="welcomeController.copyFeedback || t('welcome.copyCloneCommand')"></span>
                    </button>
                </div>
            </div>
            <div class="mt-8 pt-6 border-t border-gray-800 text-center text-xs text-gray-500" x-text="t('welcome.footerCopyright')"></div>
        </div>
    </footer>
</div>
`,Ei=`<div class="space-y-4 max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">

    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white" x-text="t('landing.title')"></h1>
    <button @click="logout" 
            class="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors duration-200"
            x-text="t('common.logout')">
    </button>
    <button @click="currentPage.fetchProtectedData()" 
            class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading" x-text="t('landing.fetchProtected')"></span>
        <span x-show="currentPage.isLoading" x-text="t('common.loading')"></span>
    </button>
    <button @click="currentPage.fetchPublicData()" 
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading" x-text="t('landing.fetchPublic')"></span>
        <span x-show="currentPage.isLoading" x-text="t('common.loading')"></span>
    </button>

    <button @click="loadPage('view-container', 'testpage');" 
            class="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors duration-200 disabled:opacity-50"
            :disabled="currentPage.isLoading">
        <span x-show="!currentPage.isLoading" x-text="t('landing.loadTestPage')"></span>
        <span x-show="currentPage.isLoading" x-text="t('common.loading')"></span>
    </button>

    <div x-show="currentPage.error" 
        class="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md" 
        x-text="currentPage.error">
    </div>

    <div x-show="currentPage.response" class="mt-4">
        <h2 class="text-lg font-semibold mb-2 text-gray-800 dark:text-white" x-text="t('common.response')"></h2>
        <pre class="bg-gray-100 dark:bg-gray-700 p-4 rounded-md overflow-x-auto text-gray-800 dark:text-gray-200" x-text="JSON.stringify(currentPage.response, null, 2)"></pre>
    </div>

</div>
`,Ai=`<button @click="currentPage.ttt(); loadPage('view-container', 'landingpage');" 
        x-init="currentPage.abc = 27;"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50"
        :disabled="currentPage.isLoading">
    <span x-show="!currentPage.isLoading" x-text="t('testpage.loadLanding')"></span>
    <span x-show="currentPage.isLoading" x-text="t('common.loading')"></span>
</button>
`,A={menu:{template:_i,controller:Zn,seo:{visibility:"app",titleKey:"seo.menu.title"}},login:{template:ki,controller:_e,seo:{visibility:"auth",titleKey:"seo.login.title",descriptionKey:"seo.frameworkDescription"}},user_registry:{template:Si,controller:yi,seo:{visibility:"auth",titleKey:"seo.register.title",descriptionKey:"seo.frameworkDescription"}},welcome:{template:Ci,controller:tt,seo:{visibility:"public",titleKey:"seo.welcome.title",descriptionKey:"seo.welcome.description"}},landingpage:{template:Ei,controller:bi,seo:{visibility:"app",titleKey:"seo.landing.title",descriptionKey:"seo.frameworkDescription"}},testpage:{template:Ai,controller:vi,seo:{visibility:"app",titleKey:"seo.testpage.title"}}},Pi={loading:"Loading...",processing:"Processing...",login:"Login",logout:"Logout",register:"Register",response:"Response:",language:"Language",toggleDarkMode:"Toggle dark mode",darkMode:"Dark Mode",lightMode:"Light Mode",orContinueWith:"or continue with"},Oi={appName:"Vanilla App",dashboard:"Dashboard",analytics:"Analytics",settings:"Settings",profile:"Profile",logout:"Logout"},Ti={backToWelcome:"← Back to welcome",title:"Vanilla WebApp Demo",username:"Username",password:"Password",noAccount:"Don't have an account? Register",oauthHint:"Social login requires provider keys in .env. Restart Flask after adding them."},Ii={title:"Create an Account",username:"Username",password:"Password",confirmPassword:"Confirm Password",hasAccount:"Already have an account? Login",success:"Account created successfully! You can now login."},Li={title:"Vanilla WebApp Demo 2",fetchProtected:"Fetch Protected Data",fetchPublic:"Fetch Public Data",loadTestPage:"Load Test Page"},Ri={loadLanding:"Load Landing Page"},Mi={signIn:"Sign In",badge:"Open-source starter kit",heroTitle:"Ship your entrepreneur SaaS faster",heroSubtitle:"Flask REST API, Alpine.js SPA, JWT + OAuth, SEO modes, and Docker — a production-ready starter so you focus on your idea, not boilerplate.",copyCommand:"Copy command",copyCloneCommand:"Copy clone command",copied:"Copied!",copyUnavailable:"Copy unavailable",copyFailed:"Copy failed",trustAuth:"Auth & OAuth ready",trustVite:"Vite + Tailwind",trustAlembic:"Alembic migrations",trustDocker:"CI + Docker",navSeeItWork:"See it work",navFeatures:"Features",navPartners:"Partners",carouselTitle:"Built for real products",carouselSubtitle:"Everything below ships in the box — no add-ons required.",carouselPrev:"Previous slide",carouselNext:"Next slide",carouselSlide1Label:"Go to slide 1",carouselSlide2Label:"Go to slide 2",carouselSlide3Label:"Go to slide 3",carouselSlide4Label:"Go to slide 4",slide1Tag:"Dev workflow",slide1Title:"Dual-server, one origin",slide1Desc:"Vite proxies /api to Flask — zero CORS pain.",slide2SignIn:"Sign in",slide2Or:"or",slide2Google:"Continue with Google",slide2Facebook:"Continue with Facebook",slide3Swagger:"Interactive Swagger UI — every route documented.",featuresEyebrow:"Why this stack",featuresTitle:"Why founders choose it",featureBackendTitle:"Backend-first",featureBackendDesc:"Models, blueprints, pytest coverage, and Alembic before you touch UI.",featureFrontendTitle:"Vanilla frontend",featureFrontendDesc:"Alpine.js controllers + Handlebars templates — no framework lock-in.",featureSeoTitle:"SEO fork-ready",featureSeoDesc:"auth-first or public-first modes with /robots.txt and page metadata.",partnersTitle:"Partners",partnersRecommended:"Recommended tools",partnersSubtitle:"Affiliate picks for your stack",partnerHosting:"Hosting",partnerDoTitle:"DigitalOcean App Platform",partnerDoDesc:"$200 credit · managed SSL",partnerDomain:"Domain",partnerNcTitle:"Namecheap .com",partnerNcDesc:"DNS ready for OAuth redirects",affiliateNotice:"Contains affiliate links",adSponsored:"Sponsored",adSlot:"Ad slot",adMediumRect:"Medium rectangle",adDisplayBanner:"Display banner",footerTagline:"Fork it, set your .env, and ship.",footerGithub:"View on GitHub",footerCopyright:"© 2026 Vanilla WebApp Framework · Built with Flask, Alpine.js & Tailwind"},Di={USERNAME_REQUIRED:"Username is required",PASSWORD_REQUIRED:"Password is required",PASSWORD_TOO_SHORT:"Password must be at least 6 characters",PASSWORDS_DO_NOT_MATCH:"Passwords do not match",LOGIN_FAILED:"Login failed. Please try again.",REGISTRATION_FAILED:"Registration failed. Please try again.",REQUEST_FAILED:"Request failed",NOT_LOGGED_IN:"Not logged in",UNAUTHORIZED:"Unauthorized",FETCH_FAILED:"Failed to fetch data",HTTP_ERROR:"Error: {status}",TOKEN_MISSING:"Token is missing",TOKEN_EXPIRED:"Token has expired",INVALID_TOKEN:"Invalid token",INVALID_CREDENTIALS:"Invalid credentials",USERNAME_PASSWORD_REQUIRED:"Username and password are required",USERNAME_EXISTS:"Username already exists",REGISTRATION_FAILED_SERVER:"Registration failed due to a server error",PROVIDER_NOT_CONFIGURED:"Provider not configured",NOT_FOUND:"Not found",INTERNAL_ERROR:"Internal server error",AUTH_FAILED:"Authentication failed",OAUTH_NOT_CONFIGURED:"{provider} login is not configured. Add {envPrefix}_CLIENT_ID and {envPrefix}_CLIENT_SECRET to .env, then restart Flask.",UNKNOWN_ERROR:"An unexpected error occurred"},Ni={frameworkDescription:"Vanilla WebApp Framework — lightweight Flask and Alpine.js starter for entrepreneur solutions.",menu:{title:"Menu — Vanilla WebApp Demo"},login:{title:"Login — Vanilla WebApp Demo"},register:{title:"Register — Vanilla WebApp Demo"},welcome:{title:"Vanilla WebApp Framework — Ship your SaaS faster",description:"Vanilla WebApp Framework — lightweight Flask and Alpine.js starter for entrepreneur solutions."},landing:{title:"Vanilla WebApp Demo"},testpage:{title:"Test Page — Vanilla WebApp Demo"}},Fi={common:Pi,menu:Oi,login:Ti,register:Ii,landing:Li,testpage:Ri,welcome:Mi,errors:Di,seo:Ni},ji={loading:"Carregando...",processing:"Processando...",login:"Entrar",logout:"Sair",register:"Cadastrar",response:"Resposta:",language:"Idioma",toggleDarkMode:"Alternar modo escuro",darkMode:"Modo escuro",lightMode:"Modo claro",orContinueWith:"ou continue com"},Bi={appName:"Vanilla App",dashboard:"Painel",analytics:"Análises",settings:"Configurações",profile:"Perfil",logout:"Sair"},$i={backToWelcome:"← Voltar ao início",title:"Demo Vanilla WebApp",username:"Usuário",password:"Senha",noAccount:"Não tem conta? Cadastre-se",oauthHint:"Login social requer chaves de provedor no .env. Reinicie o Flask após adicioná-las."},Ui={title:"Criar uma conta",username:"Usuário",password:"Senha",confirmPassword:"Confirmar senha",hasAccount:"Já tem conta? Entrar",success:"Conta criada com sucesso! Agora você pode entrar."},Wi={title:"Demo Vanilla WebApp 2",fetchProtected:"Buscar dados protegidos",fetchPublic:"Buscar dados públicos",loadTestPage:"Carregar página de teste"},Vi={loadLanding:"Carregar página inicial"},Hi={signIn:"Entrar",badge:"Kit inicial open-source",heroTitle:"Lance seu SaaS empreendedor mais rápido",heroSubtitle:"API REST Flask, SPA Alpine.js, JWT + OAuth, modos SEO e Docker — um starter pronto para produção para você focar na sua ideia, não em boilerplate.",copyCommand:"Copiar comando",copyCloneCommand:"Copiar comando clone",copied:"Copiado!",copyUnavailable:"Cópia indisponível",copyFailed:"Falha ao copiar",trustAuth:"Auth e OAuth prontos",trustVite:"Vite + Tailwind",trustAlembic:"Migrações Alembic",trustDocker:"CI + Docker",navSeeItWork:"Veja funcionando",navFeatures:"Recursos",navPartners:"Parceiros",carouselTitle:"Feito para produtos reais",carouselSubtitle:"Tudo abaixo já vem na caixa — sem complementos.",carouselPrev:"Slide anterior",carouselNext:"Próximo slide",carouselSlide1Label:"Ir para slide 1",carouselSlide2Label:"Ir para slide 2",carouselSlide3Label:"Ir para slide 3",carouselSlide4Label:"Ir para slide 4",slide1Tag:"Fluxo de dev",slide1Title:"Dois servidores, uma origem",slide1Desc:"Vite faz proxy de /api para Flask — zero dor de CORS.",slide2SignIn:"Entrar",slide2Or:"ou",slide2Google:"Continuar com Google",slide2Facebook:"Continuar com Facebook",slide3Swagger:"Swagger UI interativo — cada rota documentada.",featuresEyebrow:"Por que esta stack",featuresTitle:"Por que fundadores escolhem",featureBackendTitle:"Backend primeiro",featureBackendDesc:"Models, blueprints, cobertura pytest e Alembic antes de tocar na UI.",featureFrontendTitle:"Frontend vanilla",featureFrontendDesc:"Controllers Alpine.js + templates Handlebars — sem lock-in de framework.",featureSeoTitle:"Pronto para SEO",featureSeoDesc:"Modos auth-first ou public-first com /robots.txt e metadados por página.",partnersTitle:"Parceiros",partnersRecommended:"Ferramentas recomendadas",partnersSubtitle:"Escolhas de afiliados para sua stack",partnerHosting:"Hospedagem",partnerDoTitle:"DigitalOcean App Platform",partnerDoDesc:"Crédito de $200 · SSL gerenciado",partnerDomain:"Domínio",partnerNcTitle:"Namecheap .com",partnerNcDesc:"DNS pronto para redirects OAuth",affiliateNotice:"Contém links de afiliados",adSponsored:"Patrocinado",adSlot:"Espaço publicitário",adMediumRect:"Retângulo médio",adDisplayBanner:"Banner display",footerTagline:"Faça fork, configure seu .env e lance.",footerGithub:"Ver no GitHub",footerCopyright:"© 2026 Vanilla WebApp Framework · Feito com Flask, Alpine.js e Tailwind"},Ki={USERNAME_REQUIRED:"Usuário é obrigatório",PASSWORD_REQUIRED:"Senha é obrigatória",PASSWORD_TOO_SHORT:"A senha deve ter pelo menos 6 caracteres",PASSWORDS_DO_NOT_MATCH:"As senhas não coincidem",LOGIN_FAILED:"Falha no login. Tente novamente.",REGISTRATION_FAILED:"Falha no cadastro. Tente novamente.",REQUEST_FAILED:"Falha na requisição",NOT_LOGGED_IN:"Não autenticado",UNAUTHORIZED:"Não autorizado",FETCH_FAILED:"Falha ao buscar dados",HTTP_ERROR:"Erro: {status}",TOKEN_MISSING:"Token ausente",TOKEN_EXPIRED:"Token expirado",INVALID_TOKEN:"Token inválido",INVALID_CREDENTIALS:"Credenciais inválidas",USERNAME_PASSWORD_REQUIRED:"Usuário e senha são obrigatórios",USERNAME_EXISTS:"Usuário já existe",REGISTRATION_FAILED_SERVER:"Falha no cadastro devido a erro do servidor",PROVIDER_NOT_CONFIGURED:"Provedor não configurado",NOT_FOUND:"Não encontrado",INTERNAL_ERROR:"Erro interno do servidor",AUTH_FAILED:"Falha na autenticação",OAUTH_NOT_CONFIGURED:"Login {provider} não configurado. Adicione {envPrefix}_CLIENT_ID e {envPrefix}_CLIENT_SECRET ao .env e reinicie o Flask.",UNKNOWN_ERROR:"Ocorreu um erro inesperado"},zi={frameworkDescription:"Vanilla WebApp Framework — starter leve Flask e Alpine.js para soluções empreendedoras.",menu:{title:"Menu — Demo Vanilla WebApp"},login:{title:"Entrar — Demo Vanilla WebApp"},register:{title:"Cadastro — Demo Vanilla WebApp"},welcome:{title:"Vanilla WebApp Framework — Lance seu SaaS mais rápido",description:"Vanilla WebApp Framework — starter leve Flask e Alpine.js para soluções empreendedoras."},landing:{title:"Demo Vanilla WebApp"},testpage:{title:"Página de teste — Demo Vanilla WebApp"}},Gi={common:ji,menu:Bi,login:$i,register:Ui,landing:Wi,testpage:Vi,welcome:Hi,errors:Ki,seo:zi},er=["en","pt-BR"],tr="locale",ke={en:Fi,"pt-BR":Gi};let O="en";function qi(e="en"){const t=(e||"en").toLowerCase();return t==="pt-br"||t==="pt"||t.startsWith("pt-")?"pt-BR":"en"}function Ji(){return O}function nr(e){document.documentElement.lang=e==="pt-BR"?"pt-BR":"en"}function Qi(){const e=localStorage.getItem(tr);return e&&er.includes(e)?O=e:O=qi(typeof navigator<"u"?navigator.language:"en"),nr(O),O}function Xi(e){er.includes(e)&&(O=e,localStorage.setItem(tr,e),nr(e),window.dispatchEvent(new CustomEvent("localechange",{detail:{locale:e}})))}function Se(e,t){return t.split(".").reduce((n,r)=>{if(n&&typeof n=="object"&&r in n)return n[r]},e)}function Ce(e,t={}){let n=Se(ke[O],e);return n===void 0&&O!=="en"&&(n=Se(ke.en,e)),typeof n!="string"?e:Object.entries(t).reduce((r,[o,i])=>r.replaceAll(`{${o}}`,String(i)),n)}function Yi(e){const t=Se(ke[O],`errors.${e}`)??Se(ke.en,`errors.${e}`);return typeof t=="string"?t:Ce("errors.UNKNOWN_ERROR")}const P="auth-first",Zi=new Set(["auth-first","public-first"]),ea=new Set(["public","app","auth"]);function ta(e={},t=P){const n=Zi.has(t)?t:"auth-first";return e.visibility&&ea.has(e.visibility)?e.visibility:n==="public-first"?"public":"app"}function na(e){return e==="public"}function jt(e,t){if(t==null||t==="")return;let n=document.querySelector(`meta[name="${e}"]`);n||(n=document.createElement("meta"),n.setAttribute("name",e),document.head.appendChild(n)),n.setAttribute("content",t)}function Bt(e,t){if(!t)return;let n=document.querySelector(`link[rel="${e}"]`);n||(n=document.createElement("link"),n.setAttribute("rel",e),document.head.appendChild(n)),n.setAttribute("href",t)}function F(e={},t=P){const n=ta(e,t),r=na(n),o=e.titleKey?Ce(e.titleKey):e.title,i=e.descriptionKey?Ce(e.descriptionKey):e.description;o&&(document.title=o),i&&jt("description",i),jt("robots",r?"index, follow":"noindex, nofollow"),e.canonical?Bt("canonical",e.canonical):r&&Bt("canonical",window.location.href.split("#")[0])}function ra(e){const t=window.location.hash.slice(1);if(!t)return;const n=new URLSearchParams(t),r=n.get("token"),o=n.get("auth_error");window.history.replaceState(null,"",window.location.pathname+window.location.search),r?(localStorage.setItem("token",r),e.isLoggedIn=!0):o&&(_e.error=e.tError(o),e.showLogin=!0,F(A.login.seo,P))}const oa=()=>{const e={isLoggedIn:!!localStorage.getItem("token"),showLogin:!1,oauthProviders:[],currentPage:{},activeViewPageKey:"landingpage",activeAuthPageKey:"login",locale:Qi(),menuController:Zn,loginController:_e,welcomeController:tt,t(t,n){return Ce(t,n)},tError(t){return Yi(t)},setLocale(t){Xi(t),this.locale=Ji(),this.refreshMountedPages()},refreshMountedPages(){this.isLoggedIn?(this.loadPage("menu-container","menu"),this.loadPage("view-container",this.activeViewPageKey)):this.showLogin?this.loadPage("login-register-container",this.activeAuthPageKey):this.loadPage("public-container","welcome"),this.applyInitialSeo()},showLoginPage(){this.showLogin=!0,this.refreshOAuthProviders(),F(A.login.seo,P)},showWelcomePage(){this.showLogin=!1,F(A.welcome.seo,P)},applyInitialSeo(){var t,n;this.isLoggedIn?F(((t=A[this.activeViewPageKey])==null?void 0:t.seo)??A.landingpage.seo,P):this.showLogin?F(((n=A[this.activeAuthPageKey])==null?void 0:n.seo)??A.login.seo,P):F(A.welcome.seo,P)},async refreshOAuthProviders(){try{const t=await fetch("/api/auth/providers");t.ok&&(this.oauthProviders=await t.json())}catch(t){console.error("Failed to load OAuth providers:",t)}},isOAuthEnabled(t){return this.oauthProviders.includes(t)},startSocialLogin(t){if(!this.isOAuthEnabled(t)){const n=t.charAt(0).toUpperCase()+t.slice(1);_e.error=this.t("errors.OAUTH_NOT_CONFIGURED",{provider:n,envPrefix:t.toUpperCase()});return}window.location.href=`/api/auth/${t}/login`},loadPage(t,n){const r=A[n];if(!r){console.error(`Unknown page: ${n}`);return}const o=document.getElementById(t);if(!o){console.error(`Element not found: ${t}`);return}t==="view-container"&&(this.activeViewPageKey=n),t==="login-register-container"&&(this.activeAuthPageKey=n),window.Alpine.mutateDom(()=>{o.innerHTML=r.template}),this.currentPage=Object.assign({},r.controller),typeof this.currentPage.init=="function"&&this.currentPage.init(this),Array.from(o.children).forEach(i=>{window.Alpine.initTree(i)}),t==="view-container"&&r.seo&&F(r.seo,P),n==="login"&&this.refreshOAuthProviders(),n==="welcome"&&tt.initCarousel()},bootApp(){this.loadPage("menu-container","menu"),this.loadPage("login-register-container","login"),this.loadPage("public-container","welcome"),this.loadPage("view-container","landingpage"),this.applyInitialSeo()},logout(){localStorage.removeItem("token"),window.location.href="/"}};return e.menuController.init(),e.loginController.init(e),e.welcomeController.init(),e.refreshOAuthProviders(),ra(e),window.menuController=e.menuController,window.loginController=e.loginController,window.welcomeController=e.welcomeController,e};window.Alpine=Yn;window.spaApp=oa();Yn.start();window.spaApp.bootApp();
