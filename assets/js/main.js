// Faiz-e-Islam shared JS: mobile nav, search/filter, Tasbih, Zakat calculator
document.addEventListener('DOMContentLoaded',function(){
  var btn=document.querySelector('.menu-btn'), nav=document.querySelector('nav.main');
  if(btn&&nav){btn.addEventListener('click',function(){nav.classList.toggle('open');});}
  // Surah / generic list search
  var s=document.getElementById('site-search');
  if(s){s.addEventListener('input',function(){
    var q=s.value.toLowerCase().trim();
    document.querySelectorAll('[data-search]').forEach(function(el){
      el.style.display=(!q||el.getAttribute('data-search').toLowerCase().includes(q))?'':'none';
    });
    var c=document.getElementById('search-count');
    if(c){var vis=document.querySelectorAll('[data-search]:not([style*="none"])').length;
      c.textContent=q?vis+' result(s) found':'';
    }
  });}
  // Dua category filter
  document.querySelectorAll('[data-filter]').forEach(function(b){
    b.addEventListener('click',function(){
      var f=b.getAttribute('data-filter');
      document.querySelectorAll('[data-filter]').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      document.querySelectorAll('[data-cat]').forEach(function(el){
        el.style.display=(f==='all'||el.getAttribute('data-cat')===f)?'':'none';
      });
    });
  });
  // Tasbih
  var count=0,total=0,el=document.getElementById('tasbih-count'),tot=document.getElementById('tasbih-total');
  var tap=document.getElementById('tasbih-tap'),reset=document.getElementById('tasbih-reset');
  var target=document.getElementById('tasbih-target');
  if(tap){tap.addEventListener('click',function(){count++;total++;if(el)el.textContent=count;if(tot)tot.textContent=total;
    var t=target?parseInt(target.value||'33',10):33; if(count>=t){count=0;if(el)el.textContent='0';alert('MashaAllah! Target of '+t+' reached.');}});}
  if(reset){reset.addEventListener('click',function(){count=0;total=0;if(el)el.textContent='0';if(tot)tot.textContent='0';});}
  // Zakat calculator: 2.5% of (cash+gold+silver+investments-debts) if above nisab
  var form=document.getElementById('zakat-form');
  if(form){form.addEventListener('submit',function(e){e.preventDefault();
    function v(id){return parseFloat(document.getElementById(id).value||'0')||0;}
    var total=v('z-cash')+v('z-gold')+v('z-silver')+v('z-inv')-v('z-debt');
    var nisab=parseFloat(document.getElementById('z-nisab').value||'0')||0;
    var out=document.getElementById('zakat-result');
    if(total<=0){out.innerHTML='<p>Please enter your amounts above.</p>';return;}
    if(nisab>0&&total<nisab){out.innerHTML='<p>Total wealth: <b>'+total.toLocaleString()+'</b>. This is below the nisab ('+nisab.toLocaleString()+'), so no Zakat is due this year.</p>';return;}
    out.innerHTML='<p>Total zakatable wealth: <b>'+total.toLocaleString()+'</b><br>Zakat due (2.5%): <b>'+(total*0.025).toLocaleString()+'</b></p><p class="notice">This is a guide only. For unusual assets or debts, please confirm with a qualified scholar.</p>';
  });}
});
