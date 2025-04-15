import{_ as t,a as r,b as s}from"./AddRule3-9d6ed3bf.js";import{_ as a,a as i}from"./scheme_codelint_03-5bcd9286.js";import{_ as p}from"./scheme_codelint_04-1cece3c4.js";import{_ as o,o as e,c as n,e as c}from"./app-e552612a.js";const _={},l=c('<h1 id="代码检查-规则配置" tabindex="-1"><a class="header-anchor" href="#代码检查-规则配置" aria-hidden="true">#</a> 代码检查-规则配置</h1><p>在上一节文档<strong>代码检查配置</strong>中我们大致已经了解规则配置主要由<strong>官方规则包</strong>和<strong>自定义规则包</strong>构成，本节将详细描述规则配置。</p><p><strong>官方规则包</strong>是由腾讯云代码分析平台经过多年深耕，在业务中不断实践整理而出的规则集合包，然而平台有超过**10000+**的规则，有些规则并未放到官方规则包中，甚至有些规则是由用户自定义的规则。此外，有些官方规则包中的规则，对于不同的团队所需可能存在差异，因此产生了如下几种问题：</p><ul><li><p><strong>在规则配置中，如何添加规则？</strong></p></li><li><p><strong>在规则配置中，如果将官方规则包中的规则进行调整？</strong></p></li></ul><h2 id="在规则配置中-如何添加规则" tabindex="-1"><a class="header-anchor" href="#在规则配置中-如何添加规则" aria-hidden="true">#</a> 在规则配置中，如何添加规则？</h2><p>添加规则存在<strong>两种入口</strong>：</p><div class="custom-container tip"><p class="custom-container-title">提示</p><p>无论何种，最终都是将规则添加到自定义规则包中</p></div><ul><li><p>用户可直接点击页面中的添加规则</p><p><img src="'+t+'" alt="添加规则配置"></p></li><li><p>用户可点击自定义规则，进入自定义规则包后，再点击添加规则</p><p><img src="'+a+'" alt="点击自定义规则包"></p><p><img src="'+i+'" alt="添加规则"></p></li></ul><p>在添加规则过程中，可以单选或者批量多选规则，可以根据搜索栏进行多维度查询规则</p><p><img src="'+r+'" alt="添加规则配置"></p><p><img src="'+s+'" alt="添加规则配置"></p><h2 id="在规则配置中-如果将官方规则包中的规则进行调整" tabindex="-1"><a class="header-anchor" href="#在规则配置中-如果将官方规则包中的规则进行调整" aria-hidden="true">#</a> 在规则配置中，如果将官方规则包中的规则进行调整？</h2><p>用户可以点击进入官方规则包，进入官方规则包中，对已存在的规则进行编辑。</p><div class="custom-container warning"><p class="custom-container-title">注意</p><p>在官方规则包中对规则的任意操作，实质上是将对应规则增加到自定义规则包中进行了相关操作。</p><p>自定义规则包中的规则配置会默认覆盖其他官方包中相同规则的配置。</p></div><p><img src="'+p+'" alt="编辑官方规则包规则"></p>',15),m=[l];function d(h,g){return e(),n("div",null,m)}const b=o(_,[["render",d],["__file","代码检查规则配置.html.vue"]]);export{b as default};
