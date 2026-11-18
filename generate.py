#!/usr/bin/env python3
"""Build the Faiz-e-Islam multi-page static site.
Fetches Quran text live from AlQuran.cloud (Arabic + ur.junagarhi + en.sahih)
and generates 114 Surah pages plus all section pages. No WordPress.
Run: python3 /tmp/build_site.py
"""
import json, os, re, time, urllib.request, html

ROOT = os.path.expanduser("~/workspace/faiz-e-islam-site")
CACHE = "/tmp/quran_data"
os.makedirs(CACHE, exist_ok=True)

SLUGS = """al-fatiha al-baqarah aal-e-imran an-nisa al-maidah al-anam al-araf al-anfal
at-tawbah yunus hud yusuf ar-rad ibrahim al-hijr an-nahl al-isra al-kahf maryam
taha al-anbiya al-hajj al-muminun an-nur al-furqan ash-shuara an-naml al-qasas
al-ankabut ar-rum luqman as-sajdah al-ahzab saba fatir yaseen as-saffat saad
az-zumar ghafir fussilat ash-shura az-zukhruf ad-dukhan al-jasia al-ahqaf
muhammad al-fath al-hujurat qaf az-zariyat at-tur an-najm al-qamar ar-rahman
al-waqiah al-hadid al-mujadilah al-hashr al-mumtahinah as-saff al-jumuah
al-munafiqun at-taghabun at-talaq at-tahrim al-mulk al-qalam al-haqqah
al-maarij nuh al-jinn al-muzzammil al-muddaththir al-qiyamah al-insan
al-mursalat an-naba an-naziat abasa at-takwir al-infitar al-mutaffifin
al-inshiqaq al-buruj at-tariq al-ala al-ghashiyah al-fajr al-balad ash-shams
al-lail ad-duha ash-sharh at-tin al-alaq al-qadr al-bayyinah az-zalzalah
al-adiyat al-qariah at-takathur al-asr al-humazah al-fil quraish al-maun
al-kauthar al-kafirun an-nasr al-lahab al-ikhlas al-falaq an-nas""".split()
assert len(SLUGS) == 114, len(SLUGS)

def esc(s):
    return html.escape(s or "", quote=True)

def fetch_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Faiz-e-Islam-site-builder/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)["data"]
        except Exception as e:
            print("  retry", url, e); time.sleep(1.5 * (i + 1))
    raise RuntimeError("failed: " + url)

def get_surah(n):
    """Return (arabic, urdu, english) surah dicts, cached in /tmp."""
    out = []
    for ed in ["", "ur.junagarhi", "en.sahih"]:
        p = os.path.join(CACHE, f"surah-{n}-{ed or 'ar'}.json")
        if os.path.exists(p):
            out.append(json.load(open(p)))
        else:
            url = f"https://api.alquran.cloud/v1/surah/{n}" + (f"/{ed}" if ed else "")
            d = fetch_json(url)
            json.dump(d, open(p, "w"))
            out.append(d)
            time.sleep(0.05)
    return out

CSS = r"""/* Faiz-e-Islam — green + gold, mobile first */
:root{--green:#0b6b3a;--green-dark:#064d28;--gold:#c9a227;--gold-light:#f5e9c8;
--ink:#1f2937;--muted:#5b6470;--bg:#fffdf6;--card:#fff;--line:#e5ddc3;
--radius:14px;--max:1100px}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.65}
a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}
h1,h2,h3{color:var(--green-dark);line-height:1.3}
header.site{background:var(--green-dark);color:#fff;position:sticky;top:0;z-index:50}
.header-in{max-width:var(--max);margin:0 auto;display:flex;align-items:center;gap:16px;padding:10px 16px;flex-wrap:wrap}
.logo{font-size:1.5rem;font-weight:800;color:#fff;letter-spacing:.3px}
.logo span{color:var(--gold)}
nav.main{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
nav.main a{color:#e7f5ec;padding:8px 10px;border-radius:8px;font-size:.95rem}
nav.main a:hover,nav.main a.active{background:#ffffff22;text-decoration:none;color:#fff}
.menu-btn{display:none;background:var(--gold);border:0;border-radius:8px;padding:8px 12px;font-size:1rem;cursor:pointer;margin-left:auto}
.hero{background:linear-gradient(135deg,#064d28,#0b6b3a 55%,#0f7a45);color:#fff;text-align:center;padding:56px 16px 48px}
.hero h1{color:#fff;font-size:2.2rem;margin:0 0 10px}.hero p{max-width:720px;margin:0 auto 20px;color:#e7f5ec;font-size:1.1rem}
.btn{display:inline-block;background:var(--gold);color:#231a00;font-weight:700;padding:11px 22px;border-radius:999px;margin:4px}
.btn.ghost{background:transparent;color:#fff;border:2px solid #fff}
.btn:hover{text-decoration:none;opacity:.92}
main{max-width:var(--max);margin:0 auto;padding:24px 16px 48px}
section{margin-bottom:40px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.card h3{margin-top:0}.card p{color:var(--muted)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.arabic{font-family:"Amiri","Scheherazade New",serif;font-size:1.7rem;line-height:2.1;direction:rtl;text-align:right;color:#111}
.ayah{border:1px solid var(--line);border-radius:var(--radius);background:#fff;padding:16px 18px;margin:14px 0}
.ayah .num{font-weight:800;color:var(--green)} .ayah .urdu{direction:rtl;text-align:right;font-family:"Noto Nastaliq Urdu",serif;line-height:2}
.facts{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.facts span{background:var(--gold-light);border:1px solid var(--gold);border-radius:999px;padding:6px 14px;font-size:.92rem}
input[type=search],input[type=text],input[type=number],input[type=email],textarea,select{width:100%;padding:11px 12px;border:1px solid #cbd5d1;border-radius:10px;font-size:1rem}
.search-box{max-width:520px;margin:0 0 18px}
.surah-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.surah-list a{display:block;background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.surah-list a:hover{border-color:var(--gold);text-decoration:none}
.surah-list .n{font-weight:800;color:var(--green);margin-right:8px}
table{width:100%;border-collapse:collapse;background:#fff}th,td{border:1px solid var(--line);padding:9px 10px;text-align:left}
th{background:var(--green);color:#fff}
footer.site{background:var(--green-dark);color:#d7ead d;color:#d7eadd;margin-top:20px}
.footer-in{max-width:var(--max);margin:0 auto;padding:32px 16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px}
footer.site a{color:#ffe9a8}footer.site h3{color:#fff}
.copy{text-align:center;padding:14px;border-top:1px solid #ffffff22;color:#bcd8c6;font-size:.9rem}
.tasbih-big{font-size:3.4rem;font-weight:800;text-align:center;color:var(--green-dark)}
.tasbih-btn{display:block;width:220px;height:220px;margin:12px auto;border-radius:50%;background:var(--green);color:#fff;font-size:1.3rem;border:8px solid var(--gold);cursor:pointer}
.faq details{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:10px 0}
.faq summary{font-weight:700;cursor:pointer;color:var(--green-dark)}
.audio-box{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:16px;margin:18px 0}
.audio-box audio{width:100%}
.breadcrumb{font-size:.9rem;color:var(--muted);margin-bottom:8px}
.notice{background:#fff8e1;border:1px solid var(--gold);border-radius:10px;padding:12px 16px}
@media(max-width:760px){.menu-btn{display:block}nav.main{display:none;width:100%;flex-direction:column}
nav.main.open{display:flex}.hero h1{font-size:1.6rem}.grid2{grid-template-columns:1fr}.arabic{font-size:1.45rem}}
"""

JS = r"""// Faiz-e-Islam shared JS: mobile nav, search/filter, Tasbih, Zakat calculator
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
"""

# ---------- shared page template ----------
NAV = [("index.html","Home"),("al-quran.html","Al Quran"),("durood.html","Durood"),
("kalimas.html","Kalimas"),("salaat.html","Salaat"),("duas.html","Duas"),
("istikhara.html","Istikhara"),("blogs.html","Blogs"),("naat.html","Naat"),
("wazaif.html","Wazaif"),("names.html","99 Names"),("zakat.html","Zakat"),
("tasbih.html","Tasbih"),("quran-classes.html","Quran Classes"),("about.html","About"),
("contact.html","Contact"),("donate.html","Donate")]

def header(root, active=""):
    links = "".join(f'<a href="{root}{u}" class="{"active" if u==active else ""}">{t}</a>' for u, t in NAV)
    return f"""<header class="site"><div class="header-in">
<a class="logo" href="{root}index.html">Faiz <span>e Islam</span></a>
<button class="menu-btn" aria-label="Menu">&#9776; Menu</button>
<nav class="main">{links}</nav></div></header>"""

FOOTER = """<footer class="site"><div class="footer-in">
<div><h3>Faiz e Islam</h3><p>Read the Holy Quran, Durood, Surahs, Duas, Kalimas and Salaat online — free for everyone, with Urdu and English translation and audio.</p></div>
<div><h3>Quick Links</h3><p><a href="{r}about.html">About Us</a><br><a href="{r}blogs.html">Islamic Blogs</a><br><a href="{r}contact.html">Contact Us</a><br><a href="{r}donate.html">Donate</a><br><a href="{r}privacy-policy.html">Privacy Policy</a></p></div>
<div><h3>Most Read Surahs</h3><p><a href="{r}al-quran/surah-yaseen.html">Surah Yaseen</a><br><a href="{r}al-quran/surah-ar-rahman.html">Surah Ar-Rahman</a><br><a href="{r}al-quran/surah-al-mulk.html">Surah Al-Mulk</a><br><a href="{r}al-quran/surah-al-kahf.html">Surah Al-Kahf</a><br><a href="{r}al-quran/surah-al-waqiah.html">Surah Al-Waqiah</a></p></div>
<div><h3>Categories</h3><p><a href="{r}al-quran.html">Al Quran</a><br><a href="{r}durood.html">Durood Sharif</a><br><a href="{r}naat.html">Naat Lyrics</a><br><a href="{r}wazaif.html">Wazaif</a><br><a href="{r}duas.html">Daily Duas</a></p></div>
</div><div class="copy">&copy; 2026 Faiz e Islam. All resources are free. Quran text and translations: AlQuran.cloud.</div></footer>
<script src="{r}assets/js/main.js"></script></body></html>"""

def page(root, title, desc, body, active=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Faiz e Islam</title><meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{root}assets/css/style.css">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
</head><body>
{header(root, active)}
<main>{body}</main>
{FOOTER.format(r=root)}"""

def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)
    return p

NAMES99 = [
("Allah","اللهُ","The God — the only one worthy of worship"),
("Ar-Rahman","الرَّحْمَنُ","The Most Merciful"),("Ar-Raheem","الرَّحِيمُ","The Most Compassionate"),
("Al-Malik","الْمَلِكُ","The King"),("Al-Quddus","الْقُدُّوسُ","The Most Holy"),
("As-Salam","السَّلَامُ","The Source of Peace"),("Al-Mumin","الْمُؤْمِنُ","The Giver of Faith"),
("Al-Muhaymin","الْمُهَيْمِنُ","The Guardian"),("Al-Aziz","الْعَزِيزُ","The Almighty"),
("Al-Jabbar","الْجَبَّارُ","The Compeller"),("Al-Mutakabbir","الْمُتَكَبِّرُ","The Supreme"),
("Al-Khaliq","الْخَالِقُ","The Creator"),("Al-Bari","الْبَارِئُ","The Originator"),
("Al-Musawwir","الْمُصَوِّرُ","The Fashioner"),("Al-Ghaffar","الْغَفَّارُ","The Great Forgiver"),
("Al-Qahhar","الْقَهَّارُ","The Irresistible"),("Al-Wahhab","الْوَهَّابُ","The Bestower"),
("Ar-Razzaq","الرَّزَّاقُ","The Provider"),("Al-Fattah","الْفَتَّاحُ","The Opener"),
("Al-Aleem","الْعَلِيمُ","The All-Knowing"),("Al-Qabid","الْقَابِضُ","The Withholder"),
("Al-Basit","الْبَاسِطُ","The Extender"),("Al-Khafid","الْخَافِضُ","The Abaser"),
("Ar-Rafi","الرَّافِعُ","The Exalter"),("Al-Muizz","الْمُعِزُّ","The Honourer"),
("Al-Mudhill","الْمُذِلُّ","The Humiliator"),("As-Sami","السَّمِيعُ","The All-Hearing"),
("Al-Basir","الْبَصِيرُ","The All-Seeing"),("Al-Hakam","الْحَكَمُ","The Judge"),
("Al-Adl","الْعَدْلُ","The Just"),("Al-Latif","اللَّطِيفُ","The Subtle One"),
("Al-Khabir","الْخَبِيرُ","The All-Aware"),("Al-Halim","الْحَلِيمُ","The Forbearing"),
("Al-Azim","الْعَظِيمُ","The Magnificent"),("Al-Ghafoor","الْغَفُورُ","The All-Forgiving"),
("Ash-Shakur","الشَّكُورُ","The Appreciative"),("Al-Aliyy","الْعَلِيُّ","The Most High"),
("Al-Kabir","الْكَبِيرُ","The Most Great"),("Al-Hafiz","الْحَفِيظُ","The Preserver"),
("Al-Muqit","الْمُقِيتُ","The Sustainer"),("Al-Hasib","الْحَسِيبُ","The Reckoner"),
("Al-Jalil","الْجَلِيلُ","The Majestic"),("Al-Karim","الْكَرِيمُ","The Generous"),
("Ar-Raqib","الرَّقِيبُ","The Watchful"),("Al-Mujib","الْمُجِيبُ","The Responsive"),
("Al-Wasi","الْوَاسِعُ","The All-Encompassing"),("Al-Hakim","الْحَكِيمُ","The All-Wise"),
("Al-Wadud","الْوَدُودُ","The Most Loving"),("Al-Majid","الْمَجِيدُ","The Glorious"),
("Al-Baith","الْبَاعِثُ","The Resurrector"),("Ash-Shahid","الشَّهِيدُ","The Witness"),
("Al-Haqq","الْحَقُّ","The Truth"),("Al-Wakil","الْوَكِيلُ","The Trustee"),
("Al-Qawiyy","الْقَوِيُّ","The Strong"),("Al-Matin","الْمَتِينُ","The Firm"),
("Al-Waliyy","الْوَلِيُّ","The Protector"),("Al-Hamid","الْحَمِيدُ","The Praiseworthy"),
("Al-Muhsi","الْمُحْصِي","The Counter"),("Al-Mubdi","الْمُبْدِئُ","The Originator"),
("Al-Muid","الْمُعِيدُ","The Restorer"),("Al-Muhyi","الْمُحْيِي","The Giver of Life"),
("Al-Mumit","الْمُمِيتُ","The Bringer of Death"),("Al-Hayy","الْحَيُّ","The Ever-Living"),
("Al-Qayyum","الْقَيُّومُ","The Self-Subsisting"),("Al-Wajid","الْوَاجِدُ","The Perceiver"),
("Al-Majid","الْمَاجِدُ","The Illustrious"),("Al-Wahid","الْوَاحِدُ","The One"),
("As-Samad","الصَّمَدُ","The Eternal"),("Al-Qadir","الْقَادِرُ","The Capable"),
("Al-Muqtadir","الْمُقْتَدِرُ","The Powerful"),("Al-Muqaddim","الْمُقَدِّمُ","The Expediter"),
("Al-Muakhkhir","الْمُؤَخِّرُ","The Delayer"),("Al-Awwal","الْأَوَّلُ","The First"),
("Al-Akhir","الْآخِرُ","The Last"),("Az-Zahir","الظَّاهِرُ","The Manifest"),
("Al-Batin","الْبَاطِنُ","The Hidden"),("Al-Wali","الْوَالِي","The Governor"),
("Al-Mutaali","الْمُتَعَالِي","The Most Exalted"),("Al-Barr","الْبَرُّ","The Source of Goodness"),
("At-Tawwab","التَّوَّابُ","The Acceptor of Repentance"),("Al-Muntaqim","الْمُنْتَقِمُ","The Avenger"),
("Al-Afuww","الْعَفُوُّ","The Pardoner"),("Ar-Rauf","الرَّؤُوفُ","The Most Kind"),
("Malik-ul-Mulk","مَالِكُ الْمُلْكِ","Master of the Kingdom"),("Dhul-Jalali-wal-Ikram","ذُو الْجَلَالِ وَالْإِكْرَامِ","Lord of Majesty and Honour"),
("Al-Muqsit","الْمُقْسِطُ","The Equitable"),("Al-Jami","الْجَامِعُ","The Gatherer"),
("Al-Ghaniyy","الْغَنِيُّ","The Self-Sufficient"),("Al-Mughni","الْمُغْنِي","The Enricher"),
("Al-Mani","الْمَانِعُ","The Preventer"),("Ad-Darr","الضَّارُّ","The Distresser"),
("An-Nafi","النَّافِعُ","The Benefactor"),("An-Nur","النُّورُ","The Light"),
("Al-Hadi","الْهَادِي","The Guide"),("Al-Badi","الْبَدِيعُ","The Incomparable"),
("Al-Baqi","الْبَاقِي","The Everlasting"),("Al-Warith","الْوَارِثُ","The Inheritor"),
("Ar-Rashid","الرَّشِيدُ","The Guide to Right Path"),("As-Sabur","الصَّبُورُ","The Patient"),
]
assert len(NAMES99) == 99, len(NAMES99)

KALIMAS = [
("1st Kalima — Tayyab","لَا إِلٰهَ إِلَّا اللهُ مُحَمَّدٌ رَسُولُ اللهِ",
 "La ilaha illallah, Muhammadur Rasulullah.",
 "There is no god but Allah, and Muhammad is the Messenger of Allah.",
 "اللہ کے سوا کوئی معبود نہیں، محمد ﷺ اللہ کے رسول ہیں۔",
 "The declaration of faith — the foundation of Islam. Whoever says it with sincerity enters the fold of Islam."),
("2nd Kalima — Shahadat","أَشْهَدُ أَنْ لَا إِلٰهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ",
 "Ashhadu an la ilaha illallah, wahdahu la sharika lah, wa ashhadu anna Muhammadan abduhu wa rasuluh.",
 "I bear witness that there is no god but Allah, alone, without partner, and I bear witness that Muhammad is His servant and Messenger.",
 "میں گواہی دیتا ہوں کہ اللہ کے سوا کوئی معبود نہیں، وہ اکیلا ہے، اس کا کوئی شریک نہیں، اور میں گواہی دیتا ہوں کہ محمد ﷺ اس کے بندے اور رسول ہیں۔",
 "The testimony of faith, recited in every prayer and at the time of accepting Islam."),
("3rd Kalima — Tamjeed","سُبْحَانَ اللهِ وَالْحَمْدُ لِلّٰهِ وَلَا إِلٰهَ إِلَّا اللهُ وَاللهُ أَكْبَرُ وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللهِ الْعَلِيِّ الْعَظِيمِ",
 "Subhanallahi wal hamdu lillahi wa la ilaha illallahu wallahu akbar, wa la hawla wa la quwwata illa billahil aliyyil azim.",
 "Glory be to Allah, all praise is for Allah, there is no god but Allah, Allah is the Greatest, and there is no power and no strength except with Allah, the Most High, the Most Great.",
 "اللہ پاک ہے، تمام تعریف اللہ کے لیے ہے، اللہ کے سوا کوئی معبود نہیں، اللہ سب سے بڑا ہے، اور کوئی طاقت و قوت نہیں مگر اللہ کی مدد سے، جو بلند و عظیم ہے۔",
 "A kalima of praise and glorification — four great tasbihs in one sentence."),
("4th Kalima — Tauheed","لَا إِلٰهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ يُحْيِي وَيُمِيتُ وَهُوَ حَيٌّ لَا يَمُوتُ أَبَدًا أَبَدًا ذُو الْجَلَالِ وَالْإِكْرَامِ بِيَدِهِ الْخَيْرُ وَهُوَ عَلٰى كُلِّ شَيْءٍ قَدِيرٌ",
 "La ilaha illallahu wahdahu la sharika lah, lahul mulku wa lahul hamdu, yuhyi wa yumitu wa huwa hayyun la yamutu abadan abada, dhul jalali wal ikram, biyadihil khair, wa huwa ala kulli shay'in qadir.",
 "There is no god but Allah, alone, without partner. To Him belongs the kingdom and to Him belongs all praise. He gives life and causes death, and He is Ever-Living and never dies. Possessor of majesty and honour, in His hand is all good, and He has power over all things.",
 "اللہ کے سوا کوئی معبود نہیں، وہ اکیلا ہے، اس کا کوئی شریک نہیں۔ بادشاہت اسی کی ہے اور تعریف اسی کے لیے ہے۔ وہ زندہ کرتا ہے اور موت دیتا ہے، اور وہ ہمیشہ زندہ ہے، کبھی نہیں مرے گا۔ وہ عظمت و بزرگی والا ہے، بھلائی اس کے ہاتھ میں ہے، اور وہ ہر چیز پر قادر ہے۔",
 "The kalima of the Oneness of Allah — a complete statement of Tawheed."),
("5th Kalima — Astaghfar","أَسْتَغْفِرُ اللهَ رَبِّي مِنْ كُلِّ ذَنْبٍ أَذْنَبْتُهُ عَمْدًا أَوْ خَطَأً سِرًّا أَوْ عَلَانِيَةً وَأَتُوبُ إِلَيْهِ مِنَ الذَّنْبِ الَّذِي أَعْلَمُ وَمِنَ الذَّنْبِ الَّذِي لَا أَعْلَمُ إِنَّكَ أَنْتَ عَلَّامُ الْغُيُوبِ وَسَتَّارُ الْعُيُوبِ وَغَفَّارُ الذُّنُوبِ وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللهِ الْعَلِيِّ الْعَظِيمِ",
 "Astaghfirullaha rabbi min kulli dhambin adhnabtuhu amdan aw khata'an, sirran aw alaniyah, wa atubu ilayhi minadh dhambil ladhi a'lamu wa minadh dhambil ladhi la a'lamu, innaka anta allamul ghuyubi wa sattarul uyubi wa ghaffarudh dhunub, wa la hawla wa la quwwata illa billahil aliyyil azim.",
 "I seek forgiveness from Allah, my Lord, for every sin I committed knowingly or unknowingly, secretly or openly, and I turn to Him in repentance from the sins I know and those I do not know. Surely You are the Knower of the unseen, the Concealer of faults and the Forgiver of sins, and there is no power and no strength except with Allah, the Most High, the Most Great.",
 "میں اپنے رب اللہ سے ہر گناہ کی معافی مانگتا ہوں جو میں نے جان بوجھ کر یا بھول کر، چھپ کر یا کھلم کھلا کیا، اور میں ان گناہوں سے توبہ کرتا ہوں جنہیں میں جانتا ہوں اور جنہیں نہیں جانتا۔ بے شک تو غیب کا جاننے والا، عیبوں کو چھپانے والا اور گناہوں کو بخشنے والا ہے۔",
 "The kalima of seeking forgiveness — recited to repent and turn back to Allah."),
("6th Kalima — Radde Kufr","اَللّٰهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ أَنْ أُشْرِكَ بِكَ شَيْئًا وَأَنَا أَعْلَمُ بِهِ وَأَسْتَغْفِرُكَ لِمَا لَا أَعْلَمُ بِهِ تُبْتُ عَنْهُ وَتَبَرَّأْتُ مِنَ الْكُفْرِ وَالشِّرْكِ وَالْكِذْبِ وَالْغِيبَةِ وَالْبِدْعَةِ وَالنَّمِيمَةِ وَالْفَوَاحِشِ وَالْبُهْتَانِ وَالْمَعَاصِي كُلِّهَا وَأَسْلَمْتُ وَأَقُولُ لَا إِلٰهَ إِلَّا اللهُ مُحَمَّدٌ رَسُولُ اللهِ",
 "Allahumma inni a'udhu bika min an ushrika bika shay'an wa ana a'lamu bihi, wa astaghfiruka lima la a'lamu bihi, tubtu anhu wa tabarra'tu minal kufri wash shirki wal kidhbi wal ghibati wal bid'ati wan namimati wal fawahishi wal buhtani wal ma'asi kulliha, wa aslamtu wa aqulu la ilaha illallahu Muhammadur Rasulullah.",
 "O Allah, I seek refuge in You from associating anything with You knowingly, and I seek Your forgiveness for what I do not know. I repent from it and I disassociate myself from disbelief, polytheism, lying, backbiting, innovation, slander, indecency, false accusation and all sins. I submit myself, and I say: there is no god but Allah, Muhammad is the Messenger of Allah.",
 "اے اللہ! میں تیری پناہ مانگتا ہوں اس سے کہ میں جان بوجھ کر تیرے ساتھ کسی کو شریک کروں، اور میں ان باتوں کی معافی مانگتا ہوں جنہیں میں نہیں جانتا۔ میں اس سے توبہ کرتا ہوں اور کفر، شرک، جھوٹ، غیبت، بدعت، چغلی، بے حیائی، بہتان اور تمام گناہوں سے بری ہوں۔ میں اسلام لایا اور کہتا ہوں: اللہ کے سوا کوئی معبود نہیں، محمد ﷺ اللہ کے رسول ہیں۔",
 "The kalima of rejecting disbelief — a renewal of faith and a turning away from all sin."),
]

# ---------- Duas (well-known, from Quran / Hisnul Muslim tradition) ----------
DUAS = [
("Morning","Dua on Waking Up","الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ",
 "Alhamdu lillahil-ladhi ahyana ba'da ma amatana wa ilayhin-nushur.",
 "All praise is for Allah who gave us life after having taken it from us, and to Him is the resurrection.",
 "تمام تعریف اللہ کے لیے ہے جس نے ہمیں موت کے بعد زندگی دی، اور اسی کی طرف لوٹنا ہے۔"),
("Morning","Dua for Knowledge","رَبِّ زِدْنِي عِلْمًا",
 "Rabbi zidni ilma.",
 "My Lord, increase me in knowledge. (Quran 20:114)",
 "اے میرے رب! میرے علم میں اضافہ فرما۔"),
("Daily Life","Dua Before Eating","بِسْمِ اللهِ وَعَلَى بَرَكَةِ اللهِ",
 "Bismillahi wa ala barakatillah.",
 "In the name of Allah and with the blessings of Allah.",
 "اللہ کے نام سے اور اللہ کی برکت سے۔"),
("Daily Life","Dua After Eating","الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ",
 "Alhamdu lillahil-ladhi at'amana wa saqana wa ja'alana muslimin.",
 "All praise is for Allah who fed us, gave us drink and made us Muslims.",
 "تمام تعریف اللہ کے لیے ہے جس نے ہمیں کھلایا، پلایا اور مسلمان بنایا۔"),
("Daily Life","Dua on Entering Home","بِسْمِ اللهِ وَلَجْنَا وَبِسْمِ اللهِ خَرَجْنَا وَعَلَى اللهِ رَبِّنَا تَوَكَّلْنَا",
 "Bismillahi walajna, wa bismillahi kharajna, wa alallahi rabbina tawakkalna.",
 "In the name of Allah we enter, in the name of Allah we leave, and upon Allah, our Lord, we place our trust.",
 "اللہ کے نام سے داخل ہوئے، اللہ کے نام سے نکلے، اور اپنے رب اللہ پر بھروسہ کیا۔"),
("Daily Life","Dua on Leaving Home","بِسْمِ اللهِ تَوَكَّلْتُ عَلَى اللهِ وَلَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللهِ",
 "Bismillahi tawakkaltu alallah, wa la hawla wa la quwwata illa billah.",
 "In the name of Allah, I place my trust in Allah, and there is no power and no strength except with Allah.",
 "اللہ کے نام سے، میں نے اللہ پر بھروسہ کیا، اور کوئی طاقت و قوت نہیں مگر اللہ کی مدد سے۔"),
("Daily Life","Dua Before Sleeping","بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
 "Bismika Allahumma amutu wa ahya.",
 "In Your name, O Allah, I die and I live.",
 "اے اللہ! تیرے نام سے مرتا ہوں اور جیتا ہوں۔"),
("Daily Life","Dua for Parents","رَبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا",
 "Rabbirhamhuma kama rabbayani saghira.",
 "My Lord, have mercy upon them as they brought me up when I was small. (Quran 17:24)",
 "اے میرے رب! ان پر رحم فرما جیسا انہوں نے بچپن میں میری پرورش کی۔"),
("Forgiveness","Sayyid-ul-Istighfar","اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ",
 "Allahumma anta rabbi, la ilaha illa anta, khalaqtani wa ana abduka, wa ana ala ahdika wa wa'dika mastata'tu, a'udhu bika min sharri ma sana'tu, abu'u laka bini'matika alayya, wa abu'u bidhanbi, faghfir li, fa innahu la yaghfirudh dhunuba illa anta.",
 "O Allah, You are my Lord, there is no god but You. You created me and I am Your servant, and I am upon Your covenant and promise as much as I am able. I seek refuge in You from the evil of what I have done. I acknowledge Your favour upon me, and I acknowledge my sin, so forgive me, for no one forgives sins except You.",
 "اے اللہ! تو میرا رب ہے، تیرے سوا کوئی معبود نہیں۔ تو نے مجھے پیدا کیا اور میں تیرا بندہ ہوں، اور میں تیرے عہد و وعدے پر قائم ہوں جتنی میری طاقت ہے۔ میں اپنے کیے کے شر سے تیری پناہ مانگتا ہوں۔ میں تیری نعمت کا اقرار کرتا ہوں اور اپنے گناہ کا اقرار کرتا ہوں، پس مجھے بخش دے، بے شک تیرے سوا کوئی گناہ نہیں بخشتا۔"),
("Forgiveness","Dua for Forgiveness","رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ",
 "Rabbana zalamna anfusana, wa in lam taghfir lana wa tarhamna lanakunanna minal khasirin.",
 "Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers. (Quran 7:23)",
 "اے ہمارے رب! ہم نے اپنی جانوں پر ظلم کیا، اور اگر تو نے ہمیں نہ بخشا اور ہم پر رحم نہ فرمایا تو ہم یقیناً نقصان اٹھانے والوں میں سے ہوں گے۔"),
("Protection","Ayat-ul-Kursi","اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ",
 "Allahu la ilaha illa huwal hayyul qayyum, la ta'khudhuhu sinatun wa la nawm, lahu ma fis samawati wa ma fil ard, man dhal-ladhi yashfa'u indahu illa bi idhnih, ya'lamu ma bayna aydihim wa ma khalfahum, wa la yuhituna bi shay'in min ilmihi illa bima sha', wasi'a kursiyyuhus samawati wal ard, wa la ya'uduhu hifzuhuma, wa huwal aliyyul azim.",
 "Allah — there is no god except Him, the Ever-Living, the Sustainer of all existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. (Quran 2:255)",
 "اللہ، اس کے سوا کوئی معبود نہیں، وہ ہمیشہ زندہ ہے، سب کو قائم رکھنے والا ہے۔ اسے نہ اونگھ آتی ہے نہ نیند۔ آسمانوں اور زمین میں جو کچھ ہے سب اسی کا ہے۔"),
("Protection","Dua for Protection","أَعُوذُ بِكَلِمَاتِ اللهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ",
 "A'udhu bikalimatillahit-tammati min sharri ma khalaq.",
 "I seek refuge in the perfect words of Allah from the evil of what He has created.",
 "میں اللہ کے کامل کلمات کی پناہ مانگتا ہوں اس کے شر سے جو اس نے پیدا کیا۔"),
("Travel","Dua for Travel","سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ وَإِنَّا إِلَى رَبِّنَا لَمُنقَلِبُونَ",
 "Subhanalladhi sakhkhara lana hadha wa ma kunna lahu muqrinin, wa inna ila rabbina lamunqalibun.",
 "Glory be to Him who has subjected this to us, and we could never have it by our efforts. And indeed, to our Lord we will return. (Quran 43:13-14)",
 "پاک ہے وہ ذات جس نے اسے ہمارے لیے مسخر کر دیا، اور ہم اسے اپنے زور سے قابو میں نہ لا سکتے تھے، اور بے شک ہم اپنے رب کی طرف لوٹنے والے ہیں۔"),
("Health","Dua for Healing","اللَّهُمَّ رَبَّ النَّاسِ أَذْهِبِ الْبَأْسَ اشْفِ أَنْتَ الشَّافِي لَا شِفَاءَ إِلَّا شِفَاؤُكَ شِفَاءً لَا يُغَادِرُ سَقَمًا",
 "Allahumma rabban-nas, adhibil ba's, ishfi antash-shafi, la shifa'a illa shifa'uk, shifa'an la yughadiru saqama.",
 "O Allah, Lord of mankind, remove the harm and heal — You are the Healer, there is no healing except Your healing, a healing that leaves no illness behind.",
 "اے اللہ! اے لوگوں کے رب! تکلیف دور فرما، شفا دے، تو ہی شفا دینے والا ہے، تیری شفا کے سوا کوئی شفا نہیں، ایسی شفا جو کوئی بیماری باقی نہ چھوڑے۔"),
("Health","Dua for Rizq (Provision)","اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا وَرِزْقًا طَيِّبًا وَعَمَلًا مُتَقَبَّلًا",
 "Allahumma inni as'aluka ilman nafi'an, wa rizqan tayyiban, wa amalan mutaqabbala.",
 "O Allah, I ask You for beneficial knowledge, good provision and accepted deeds.",
 "اے اللہ! میں تجھ سے نفع بخش علم، پاکیزہ رزق اور قبول شدہ عمل مانگتا ہوں۔"),
("Daily Life","Dua Before Wudu","بِسْمِ اللهِ",
 "Bismillah.",
 "In the name of Allah.",
 "اللہ کے نام سے۔"),
("Daily Life","Dua After Wudu","أَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ",
 "Ashhadu an la ilaha illallahu wahdahu la sharika lah, wa ashhadu anna Muhammadan abduhu wa rasuluh.",
 "I bear witness that there is no god but Allah, alone without partner, and that Muhammad is His servant and Messenger.",
 "میں گواہی دیتا ہوں کہ اللہ کے سوا کوئی معبود نہیں، وہ اکیلا ہے، اس کا کوئی شریک نہیں، اور محمد ﷺ اس کے بندے اور رسول ہیں۔"),
("Daily Life","Dua on Entering the Masjid","اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ",
 "Allahummaftah li abwaba rahmatik.",
 "O Allah, open for me the doors of Your mercy.",
 "اے اللہ! میرے لیے اپنی رحمت کے دروازے کھول دے۔"),
("Daily Life","Dua on Leaving the Masjid","اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ",
 "Allahumma inni as'aluka min fadlik.",
 "O Allah, I ask You from Your bounty.",
 "اے اللہ! میں تجھ سے تیرے فضل کا سوال کرتا ہوں۔"),
("Forgiveness","Dua of Yunus (A.S.)","لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ",
 "La ilaha illa anta, subhanaka, inni kuntu minaz-zalimin.",
 "There is no god but You, glory be to You, indeed I was among the wrongdoers. (Quran 21:87)",
 "تیرے سوا کوئی معبود نہیں، تو پاک ہے، بے شک میں ظالموں میں سے تھا۔"),
]

BLOGS = [
("hajj-2026-complete-guide","Hajj 2026 — Complete Guide, Dates and Daily Rituals",
 """<p>Hajj is the fifth pillar of Islam and a journey every Muslim dreams of making once in a lifetime. This guide explains, in plain words, what Hajj is, when it takes place in 2026, and what happens on each day from the 8th to the 13th of Dhul-Hijjah.</p>
<h2>When is Hajj 2026?</h2><p>Hajj falls in the Islamic month of Dhul-Hijjah. The main days run from the 8th to the 13th of Dhul-Hijjah. The exact Gregorian dates depend on the sighting of the moon, so pilgrims should confirm the final dates with their Hajj group and the Saudi authorities closer to the time.</p>
<h2>The five days, step by step</h2><p><b>8 Dhul-Hijjah — Day of Tarwiyah:</b> Pilgrims enter Ihram, make the intention for Hajj, and travel to Mina, where they pray Dhuhr, Asr, Maghrib and Isha and spend the night.</p>
<p><b>9 Dhul-Hijjah — Day of Arafah:</b> The most important day of Hajj. Pilgrims gather on the plain of Arafah from noon until sunset, praying and asking Allah for forgiveness. The Prophet ﷺ said Hajj is Arafah.</p>
<p><b>10 Dhul-Hijjah — Eid day:</b> After Fajr in Muzdalifah, pilgrims go to Mina, stone the largest pillar (Jamarat al-Aqaba), offer the sacrifice, shave or trim the hair, and perform Tawaf al-Ifadah in Makkah.</p>
<p><b>11–13 Dhul-Hijjah — Days of Tashreeq:</b> Pilgrims stay in Mina and stone all three pillars each day, remembering Allah and making dua.</p>
<h2>How to prepare</h2><p>Learn the rituals before you travel, keep your documents and health requirements ready, pack light, and go with patience — Hajj is a test of the body and the heart together. Above all, go with a sincere intention: Hajj is for Allah alone.</p>
<h2>Frequently asked questions</h2><p><b>Is Hajj obligatory?</b> Yes, once in a lifetime, for every Muslim who is physically and financially able.</p><p><b>Can women perform Hajj alone?</b> Rules on mahram and group travel change from time to time; check the current rules with your Hajj operator before booking.</p>"""),
("importance-of-knowledge-in-islam","The Importance of Knowledge in Islam",
 """<p>Islam begins with a command to read. The very first word revealed to the Prophet Muhammad ﷺ was <i>Iqra</i> — "Read". That one word tells us how central knowledge is in our faith: before prayer, before fasting, before any other command, Allah told His Messenger to read.</p>
<h2>Knowledge in the Quran and Hadith</h2><p>Allah says in the Quran: "Are those who know equal to those who do not know?" (39:9). The Prophet ﷺ said, "Seeking knowledge is an obligation upon every Muslim." Knowledge here is not only religious learning — it includes every useful knowledge that helps people live well and serve others.</p>
<h2>What kind of knowledge?</h2><p>First, the knowledge of our faith: the Quran, the life of the Prophet ﷺ, prayer, and the rulings we need every day. Second, the knowledge of the world: medicine, science, language, trade and craft. The early Muslim civilisation excelled in both, because it saw no wall between them.</p>
<h2>Knowledge with manners</h2><p>Knowledge without humility becomes pride. The scholars of the past taught that a student should be humble, patient and honest — and that knowledge must lead to good action. Learning a verse and living by it is better than memorising a book and ignoring it.</p>
<p>Start small and stay regular: a page of the Quran with its meaning each day, one hadith, one question asked to a teacher. Over a year, that small habit becomes a large store of knowledge.</p>"""),
("surah-yaseen-heart-of-the-quran","Surah Yaseen — The Heart of the Quran: Benefits and Overview",
 """<p>Surah Yaseen is the 36th Surah of the Holy Quran. It has 83 verses and was revealed in Makkah. Muslims know it well — it is read in the morning, at times of difficulty, and beside the sick — and it is often called the Heart of the Quran.</p>
<h2>What is Surah Yaseen about?</h2><p>The Surah begins with an oath by the wise Quran and the messengership of the Prophet ﷺ. It tells the story of a town that rejected its messengers, and of one man who ran from the far side of the city to support them. Then it turns to the signs of Allah in creation — the dead earth brought to life by rain, the night and the day, the sun and the moon in their orbits — and ends with the power of Allah to bring the dead back to life.</p>
<h2>Why do people read it every day?</h2><p>Many Muslims read Yaseen in the morning as a way to start the day with the Quran. Its verses remind us that life is short, that Allah's signs are all around us, and that the return to Him is real. Reading it slowly, with its meaning, is better than rushing through it.</p>
<h2>How to read it</h2><p>Read it with wudu, in a quiet place, verse by verse. After finishing, make dua for yourself, your family and those who have passed away. You can read it on our <a href="../al-quran/surah-yaseen.html">Surah Yaseen page</a> with Arabic, Urdu and English translation and audio.</p>"""),
("how-to-perform-umrah","How to Perform Umrah — A Complete Step-by-Step Guide",
 """<p>Umrah is the lesser pilgrimage to Makkah. Unlike Hajj, it can be performed at any time of the year. This guide walks through it in simple steps.</p>
<h2>Before you travel</h2><p>Learn the steps, arrange your visa and travel, and make a sincere intention. Pack Ihram clothes (for men, two plain white cloths), comfortable shoes, and a small bag for your valuables.</p>
<h2>The four steps of Umrah</h2><p><b>1. Ihram:</b> At the Miqat, bathe, wear Ihram, pray two rak'ahs and make the intention: "Labbayk Allahumma Umrah." Then recite the Talbiyah.</p>
<p><b>2. Tawaf:</b> In the Haram, circle the Kaaba seven times, starting at the Black Stone, praying as you walk.</p>
<p><b>3. Sa'i:</b> Walk seven times between Safa and Marwah, remembering the search of Hajar (A.S.) for water for her son Ismail (A.S.).</p>
<p><b>4. Halq or Taqsir:</b> Shave the head or trim the hair. With that, Umrah is complete and Ihram ends.</p>
<h2>After Umrah</h2><p>Pray in the Haram as much as you can, visit the Prophet's Mosque in Madinah if you are able, and carry the calm of the journey home with you — Umrah is meant to change the heart, not just the passport.</p>"""),
("sajdah-sahw","Sajdah Sahw — What to Do If You Forget How Many Rak'ahs You Prayed",
 """<p>Forgetting how many rak'ahs you have prayed happens to almost everyone. Islam has a clear remedy for it: Sajdah Sahw, the two prostrations of forgetfulness.</p>
<h2>When is Sajdah Sahw needed?</h2><p>If you add an extra rak'ah, miss a wajib act, or you are unsure whether you prayed three or four rak'ahs, Sajdah Sahw corrects the prayer. If you only doubted for a moment and then became sure, no Sajdah Sahw is needed.</p>
<h2>What to do if you are unsure of the number</h2><p>Scholars teach that when you cannot decide, you should act on the smaller number — the one you are certain about — and complete the prayer, then do Sajdah Sahw. For example, if you are unsure between three and four, count it as three, pray one more rak'ah, then do Sajdah Sahw before the Salam.</p>
<h2>How to perform it</h2><p>After the final Tashahhud, say the Salam to one side (or complete the prayer as your school teaches), then make two extra prostrations with the usual tasbih, sit, recite Tashahhud again, and end with Salam. The exact form differs slightly between schools of thought, so follow the practice of your local scholars.</p>
<p>The lesson is simple: do not abandon the prayer because of a mistake. Allah has given us a way to fix it and carry on.</p>"""),
("ramadan-a-month-of-reflection","Ramadan — A Month of Reflection, Fasting and Spiritual Renewal",
 """<p>Ramadan is the ninth month of the Islamic calendar, the month in which the Quran was first revealed. For one month, Muslims fast from dawn to sunset — no food, no drink — and turn their attention to prayer, the Quran and charity.</p>
<h2>What is fasting?</h2><p>Fasting is not only about hunger. It is training for the heart: to control the tongue, to lower the gaze, to give to others, and to remember those who have little all year round. The Prophet ﷺ said that whoever does not give up false speech and evil actions, Allah has no need of his leaving food and drink.</p>
<h2>A daily routine for Ramadan</h2><p>Begin the day with Suhoor before Fajr, pray on time, read a portion of the Quran every day — one Juz a day completes the Quran in the month — and pray Taraweeh at night. Give charity, even a little, every day, and use the last ten nights to seek Laylat-ul-Qadr, the Night of Power, which is better than a thousand months.</p>
<h2>For children and beginners</h2><p>Children can start with half-day fasts and join the family for Iftar. The goal is love for the month, not hardship. Ramadan is a guest that visits once a year — welcome it with a plan, and let it leave you better than it found you.</p>"""),
]

# ---------- static pages ----------
def static_pages():
    # HOME
    most_read = ["yaseen","ar-rahman","al-mulk","al-kahf","al-waqiah","maryam","yusuf","muhammad","al-muzzammil","al-jumuah","al-fatiha","al-ikhlas"]
    surah_names = {}
    cards = ""
    # surah names filled in main() after fetch; use slugs+numbers here via placeholder replaced later
    home = f"""<section class="hero"><h1>Read Quran, Durood, Surahs, Duas &amp; Salaat Online</h1>
<p>Faiz e Islam — a free platform to read the Holy Quran with Urdu and English translation, listen to recitation, and learn authentic Islam with clarity.</p>
<p><a class="btn" href="al-quran.html">Read Quran</a> <a class="btn ghost" href="duas.html">Daily Duas</a></p></section>
<section><h2>Al Quran</h2><p>Read all 114 Surahs of the Holy Quran with Arabic text, Urdu and English translation, and audio recitation by Mishary Rashid Alafasy. <a href="al-quran.html">Browse all 114 Surahs &rarr;</a></p></section>
<section><h2>Durood</h2><p>Sending blessings upon the Prophet Muhammad ﷺ is one of the most beloved acts of worship. Read Durood-e-Ibrahimi, Durood-e-Nariya, Durood-e-Tanjeena and Durood-e-Mahi. <a href="durood.html">Read Durood &rarr;</a></p></section>
<section><h2>Most Read Surahs</h2><div class="cards">
{''.join(f'<div class="card"><h3>Surah {s.replace("-"," ").title()}</h3><p>Read with Arabic, Urdu and English translation and audio.</p><p><a href="al-quran/surah-{s}.html">Read Surah &rarr;</a></p></div>' for s in most_read)}
</div></section>
<section><h2>Kalimas</h2><p>The Kalima, also known as the Shahada, is the fundamental declaration of faith in Islam. Read all six Kalimas with Arabic, transliteration and translation. <a href="kalimas.html">Read the Six Kalimas &rarr;</a></p></section>
<section><h2>Salaat</h2><p>Salaat is one of the five pillars of Islam and a direct way to connect with Allah. Learn Wudu, the rak'ahs of every prayer and how to pray step by step. <a href="salaat.html">Learn Salaat &rarr;</a></p></section>
<section><h2>Daily Duas</h2><p>Dua is a direct conversation with Allah — for the morning, for eating, for travel, for parents and for forgiveness. <a href="duas.html">Browse {len(DUAS)} Duas &rarr;</a></p></section>
<section><h2>Istikhara — The Prayer of Seeking Guidance</h2><p>When you face an important decision, Istikhara is the prayer of asking Allah for guidance. <a href="istikhara.html">How to perform Istikhara &rarr;</a></p></section>
<section><h2>Islamic Tools</h2><div class="cards">
<div class="card"><h3>Zakat Calculator</h3><p>Work out 2.5% Zakat on your cash, gold, silver and investments.</p><p><a href="zakat.html">Calculate Zakat &rarr;</a></p></div>
<div class="card"><h3>Digital Tasbih</h3><p>Count your dhikr with a simple counter and daily target.</p><p><a href="tasbih.html">Open Tasbih &rarr;</a></p></div>
<div class="card"><h3>99 Names of Allah</h3><p>Asma-ul-Husna with Arabic, transliteration and meaning.</p><p><a href="names.html">Read the 99 Names &rarr;</a></p></div>
<div class="card"><h3>Quran Classes</h3><p>Learn Quran online with a teacher — Noorani Qaida, Nazra, Hifz and Tajweed.</p><p><a href="quran-classes.html">Learn more &rarr;</a></p></div>
</div></section>
<section><h2>Islamic Blogs</h2><div class="cards">
{''.join(f'<div class="card"><h3>{esc(t)}</h3><p><a href="blogs/{s}.html">Read article &rarr;</a></p></div>' for s, t, _ in BLOGS[:3])}
</div><p><a href="blogs.html">All blogs &rarr;</a></p></section>"""
    write("index.html", page("", "Read Quran, Durood, Surahs, Duas & Salaat Online", "Faiz e Islam — read the Holy Quran, Durood, Surahs with audio, Duas, Kalimas and Salaat. Free Arabic text, translations and Islamic resources.", home, "index.html"))

    # KALIMAS
    kb = "<h1>The Six Kalimas</h1><p>The Kalima is the declaration of faith in Islam. Below are all six Kalimas with Arabic text, transliteration, English and Urdu translation.</p>"
    for title, ar, translit, en, ur, note in KALIMAS:
        kb += f"""<div class="card"><h2>{esc(title)}</h2><p class="arabic">{esc(ar)}</p>
<p><b>Transliteration:</b> {esc(translit)}</p><p><b>English:</b> {esc(en)}</p>
<p class="urdu"><b>Urdu:</b> {esc(ur)}</p><p>{esc(note)}</p></div>"""
    kb += """<h2>Frequently Asked Questions</h2><div class="faq">
<details><summary>How many Kalimas are there in Islam?</summary><p>There are six Kalimas: Tayyab, Shahadat, Tamjeed, Tauheed, Astaghfar and Radde Kufr.</p></details>
<details><summary>Which Kalima is recited to accept Islam?</summary><p>The first Kalima (Tayyab) and the second Kalima (Shahadat) are the declaration of faith.</p></details></div>"""
    write("kalimas.html", page("", "Six Kalimas with Urdu Translation", "Read all six Kalimas of Islam with Arabic, transliteration, English and Urdu translation.", kb, "kalimas.html"))

    # DUROOD
    db = """<h1>Durood Sharif</h1><p>Sending Durood upon the Prophet Muhammad ﷺ brings blessings, peace of heart and closeness to Allah. Below are the most read Duroods.</p>
<h2>Durood-e-Ibrahimi</h2><p>The Durood recited in every prayer, after Tashahhud.</p>
<p class="arabic">اَللّٰهُمَّ صَلِّ عَلٰى مُحَمَّدٍ وَّعَلٰى اٰلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلٰى اِبْرَاهِيْمَ وَعَلٰى اٰلِ اِبْرَاهِيْمَ اِنَّكَ حَمِيْدٌ مَّجِيْدٌ<br>
اَللّٰهُمَّ بَارِكْ عَلٰى مُحَمَّدٍ وَّعَلٰى اٰلِ مُحَمَّدٍ كَمَا بَارَكْتَ عَلٰى اِبْرَاهِيْمَ وَعَلٰى اٰلِ اِبْرَاهِيْمَ اِنَّكَ حَمِيْدٌ مَّجِيْدٌ</p>
<p><b>Transliteration:</b> Allahumma salli ala Muhammadin wa ala aali Muhammadin kama sallayta ala Ibrahima wa ala aali Ibrahima innaka Hamidum Majid. Allahumma barik ala Muhammadin wa ala aali Muhammadin kama barakta ala Ibrahima wa ala aali Ibrahima innaka Hamidum Majid.</p>
<p><b>English:</b> O Allah, send blessings upon Muhammad and upon the family of Muhammad, as You sent blessings upon Ibrahim and upon the family of Ibrahim. Indeed, You are Praiseworthy, Glorious. O Allah, bless Muhammad and the family of Muhammad, as You blessed Ibrahim and the family of Ibrahim. Indeed, You are Praiseworthy, Glorious.</p>
<h2>Durood-e-Nariya</h2><p>A well-known Durood recited for relief from difficulties and for the fulfilment of needs. It is traditionally recited 11 times or 41 times with a sincere heart, after which dua is made.</p>
<p class="arabic">اَللّٰهُمَّ صَلِّ صَلَاةً كَامِلَةً وَّسَلِّمْ سَلَامًا تَامًّا عَلٰى سَيِّدِنَا مُحَمَّدٍنِ الَّذِيْ تَنْحَلُّ بِهِ الْعُقَدُ وَتَنْفَرِجُ بِهِ الْكُرَبُ</p>
<h2>Durood-e-Tanjeena</h2><p>Known as the Durood of deliverance, recited in times of hardship and fear, seeking Allah's protection through the blessings of the Prophet ﷺ.</p>
<p class="arabic">اَللّٰهُمَّ صَلِّ عَلٰى سَيِّدِنَا مُحَمَّدٍ صَلَاةً تُنْجِيْنَا بِهَا مِنْ جَمِيْعِ الْاَهْوَالِ وَالْاٰفَاتِ</p>
<h2>Durood-e-Mahi</h2><p>A short Durood, easy to memorise and recite in large numbers after prayers and in daily dhikr.</p>
<p class="arabic">اَللّٰهُمَّ صَلِّ عَلٰى مُحَمَّدٍ وَّاٰلِهٖ وَصَحْبِهٖ وَبَارِكْ وَسَلِّمْ</p>
<h2>Why recite Durood?</h2><p>The Quran commands the believers: "Indeed, Allah and His angels send blessings upon the Prophet. O you who believe, send blessings upon him and greet him with peace." (Quran 33:56). The Prophet ﷺ said that whoever sends one blessing upon him, Allah sends ten blessings in return.</p>"""
    write("durood.html", page("", "Durood Sharif — Durood-e-Ibrahimi, Nariya, Tanjeena", "Read Durood Sharif with Arabic, transliteration and English translation.", db, "durood.html"))

    # SALAAT
    sb = """<h1>Salaat — How to Pray</h1><p>Salaat is one of the five pillars of Islam. This guide explains Wudu, the rak'ahs of each prayer and the steps of prayer, in plain words.</p>
<h2>What is Salaat?</h2><p>Salaat is the direct connection between a Muslim and Allah, performed five times a day: Fajr, Dhuhr, Asr, Maghrib and Isha. The Prophet ﷺ called it the coolness of his eyes.</p>
<h2>How to perform Wudu (Ablution), step by step</h2><ol><li>Make the intention and say Bismillah.</li><li>Wash both hands three times, up to the wrists.</li><li>Rinse the mouth three times and clean the nose three times.</li><li>Wash the face three times, from forehead to chin and ear to ear.</li><li>Wash the right forearm, then the left, up to and including the elbows, three times each.</li><li>Wipe the head once and clean the ears.</li><li>Wash the right foot, then the left, up to the ankles, three times each.</li></ol>
<h2>Rak'ahs of the five daily prayers</h2>
<table><tr><th>Prayer</th><th>Sunnah before</th><th>Fard</th><th>Sunnah after</th><th>Witr / Nafl</th></tr>
<tr><td>Fajr</td><td>2</td><td>2</td><td>—</td><td>—</td></tr>
<tr><td>Dhuhr</td><td>4</td><td>4</td><td>2 + 2 Nafl</td><td>—</td></tr>
<tr><td>Asr</td><td>4 (non-emphasised)</td><td>4</td><td>—</td><td>—</td></tr>
<tr><td>Maghrib</td><td>—</td><td>3</td><td>2 + 2 Nafl</td><td>—</td></tr>
<tr><td>Isha</td><td>4 (non-emphasised)</td><td>4</td><td>2</td><td>3 Witr</td></tr>
<tr><td>Jumu'ah (Friday)</td><td>4</td><td>2 (with Khutbah)</td><td>4 + 2</td><td>—</td></tr></table>
<h2>How to perform Salaat, step by step</h2><ol><li>Stand facing the Qibla, make the intention, and say "Allahu Akbar" (Takbir) raising both hands.</li><li>Recite Sana, then Surah Al-Fatiha, then another Surah or verses.</li><li>Bow (Ruku) saying "Subhana Rabbiyal Azim" three times.</li><li>Stand up saying "Sami'allahu liman hamidah, Rabbana lakal hamd."</li><li>Prostrate (Sajdah) saying "Subhana Rabbiyal A'la" three times, then sit, then prostrate again.</li><li>Stand for the next rak'ah and repeat. In the second rak'ah, sit for Tashahhud after the second Sajdah.</li><li>In the final sitting, recite Tashahhud, Durood-e-Ibrahimi and duas, then end with Salam to the right and to the left.</li></ol>
<h2>Common mistakes in Salaat</h2><ul><li>Rushing through the movements without pausing in each position.</li><li>Not reciting Surah Al-Fatiha in every rak'ah.</li><li>Looking around or letting the mind wander — try to understand the words you recite.</li><li>Praying without Wudu, or with clothes that do not cover properly.</li></ul>
<div class="faq"><details><summary>How many times a day do Muslims pray?</summary><p>Five times: Fajr, Dhuhr, Asr, Maghrib and Isha.</p></details>
<details><summary>What if I miss a prayer?</summary><p>Pray it as soon as you remember, with sincere repentance, and try not to delay prayers in future.</p></details></div>"""
    write("salaat.html", page("", "Salaat — How to Pray, Wudu and Rak'ahs", "Step-by-step guide to Salaat: Wudu, rak'ahs of Fajr, Dhuhr, Asr, Maghrib, Isha and Jumu'ah, and common mistakes.", sb, "salaat.html"))

    # DUAS
    cats = sorted(set(c for c, *_ in DUAS))
    ub = "<h1>Daily Duas</h1><p>Dua is a direct conversation with Allah. Below are daily duas for the morning, eating, home, travel, parents, forgiveness, protection and health — each with Arabic, transliteration and translation.</p>"
    ub += '<p>' + ' '.join(f'<button data-filter="{c}">{c}</button> <button data-filter="all">All</button>' if c == cats[0] else f'<button data-filter="{c}">{c}</button>' for c in cats) + '</p>'
    for cat, title, ar, translit, en, ur in DUAS:
        ub += f"""<div class="card" data-cat="{esc(cat)}"><h2>{esc(title)}</h2><p><b>{esc(cat)}</b></p>
<p class="arabic">{esc(ar)}</p><p><b>Transliteration:</b> {esc(translit)}</p>
<p><b>English:</b> {esc(en)}</p><p class="urdu"><b>Urdu:</b> {esc(ur)}</p></div>"""
    ub += """<h2>How to make Dua properly</h2><p>Begin with praise of Allah and Durood upon the Prophet ﷺ, ask with humility and certainty that Allah hears you, and end with Durood again. The best times for dua are in the last third of the night, between Adhan and Iqamah, in Sajdah, and on Fridays.</p>"""
    write("duas.html", page("", "Daily Duas in Islam with Urdu Translation", "40+ daily duas with Arabic, transliteration, English and Urdu translation.", ub, "duas.html"))

    # ISTIKHARA
    ib = """<h1>Istikhara — The Prayer of Seeking Guidance</h1><p>Istikhara is a beautiful prayer for anyone facing an important decision — marriage, a job, a move, or any choice where the right path is unclear. Through it, we ask Allah to guide us to what is good and to turn us away from what is harmful.</p>
<h2>Dua-e-Istikhara</h2>
<p class="arabic">اَللّٰهُمَّ إِنِّي أَسْتَخِيرُكَ بِعِلْمِكَ وَأَسْتَقْدِرُكَ بِقُدْرَتِكَ وَأَسْأَلُكَ مِنْ فَضْلِكَ الْعَظِيمِ فَإِنَّكَ تَقْدِرُ وَلَا أَقْدِرُ وَتَعْلَمُ وَلَا أَعْلَمُ وَأَنْتَ عَلَّامُ الْغُيُوبِ اَللّٰهُمَّ إِنْ كُنْتَ تَعْلَمُ أَنَّ هَذَا الْأَمْرَ خَيْرٌ لِي فِي دِينِي وَمَعَاشِي وَعَاقِبَةِ أَمْرِي فَاقْدُرْهُ لِي وَيَسِّرْهُ لِي ثُمَّ بَارِكْ لِي فِيهِ وَإِنْ كُنْتَ تَعْلَمُ أَنَّ هَذَا الْأَمْرَ شَرٌّ لِي فِي دِينِي وَمَعَاشِي وَعَاقِبَةِ أَمْرِي فَاصْرِفْهُ عَنِّي وَاصْرِفْنِي عَنْهُ وَاقْدُرْ لِيَ الْخَيْرَ حَيْثُ كَانَ ثُمَّ أَرْضِنِي بِهِ</p>
<p><b>Transliteration:</b> Allahumma inni astakhiruka bi ilmika, wa astaqdiruka bi qudratika, wa as'aluka min fadlikal azim, fa innaka taqdiru wa la aqdiru, wa ta'lamu wa la a'lamu, wa anta allamul ghuyub. Allahumma in kunta ta'lamu anna hadhal amra khayrun li fi dini wa ma'ashi wa aqibati amri, faqdurhu li wa yassirhu li thumma barik li fihi. Wa in kunta ta'lamu anna hadhal amra sharrun li fi dini wa ma'ashi wa aqibati amri, fasrifhu anni wasrifni anhu, waqdur liyal khayra haythu kana thumma ardini bihi.</p>
<p><b>English:</b> O Allah, I seek Your guidance through Your knowledge, and I seek ability through Your power, and I ask You from Your great bounty. You have power and I do not, You know and I do not, and You are the Knower of the unseen. O Allah, if You know that this matter is good for me in my religion, my livelihood and the outcome of my affair, then decree it for me, make it easy for me, and bless it for me. And if You know that this matter is bad for me in my religion, my livelihood and the outcome of my affair, then turn it away from me and turn me away from it, and decree for me what is good wherever it is, then make me content with it.</p>
<h2>How to perform Salat-ul-Istikhara, step by step</h2><ol><li>Make Wudu and pray two rak'ahs of Nafl prayer (outside the obligatory prayers).</li><li>After the prayer, recite the Dua-e-Istikhara above, naming your matter where the dua says "this matter".</li><li>Ask with a sincere heart and then go ahead — do your research, consult trustworthy people, and take the step that seems right.</li><li>Watch how matters unfold: if the path opens and your heart is at ease, that is a good sign; if doors keep closing, that too is an answer.</li></ol>
<h2>What Istikhara is not</h2><p>Istikhara is not a dream machine. You do not have to see a dream for it to work, and a dream alone is not proof. The answer usually comes as ease in one direction and difficulty in the other, or as a settled heart. Repeat the prayer for up to seven nights if the matter is still unclear.</p>
<h2>Best times</h2><p>Any time except the forbidden times for prayer (sunrise, sunset and midday). The last third of the night is a blessed time for dua.</p>
<div class="faq"><details><summary>Do I have to see a dream after Istikhara?</summary><p>No. Guidance usually comes through ease, circumstances and a settled heart, not necessarily a dream.</p></details>
<details><summary>Can I do Istikhara for someone else?</summary><p>You can pray for them, but the decision and the prayer are best made by the person concerned.</p></details></div>"""
    write("istikhara.html", page("", "Istikhara — Dua and Method", "Dua-e-Istikhara with Arabic, transliteration, translation and step-by-step method.", ib, "istikhara.html"))

    # BLOGS LIST + POSTS
    bl = "<h1>Islamic Blogs</h1><p>Articles on the Quran, Hajj, Umrah, prayer, Ramadan and the life of a Muslim — written in plain words.</p><div class='cards'>"
    for s, t, _ in BLOGS:
        bl += f'<div class="card"><h3>{esc(t)}</h3><p><a href="blogs/{s}.html">Read article &rarr;</a></p></div>'
    bl += "</div>"
    write("blogs.html", page("", "Islamic Blogs", "Islamic blogs: Hajj, Umrah, knowledge, Ramadan, prayer and more.", bl, "blogs.html"))
    for s, t, body in BLOGS:
        write(f"blogs/{s}.html", page("../", t, t, f"<p class='breadcrumb'><a href='../blogs.html'>Blogs</a> &raquo; {esc(t)}</p><h1>{esc(t)}</h1>{body}<p><a href='../blogs.html'>&larr; All blogs</a></p>", "blogs.html"))

    # NAAT
    nb = """<h1>Naat Lyrics</h1><p>Naat lyrics to read and sing in praise of the Prophet Muhammad ﷺ.</p>
<h2>Tajdar-e-Haram</h2><p><i>Tajdar-e-Haram, ho nigah-e-karam, hum ghareebon ke din bhi sanwar jayenge.<br>
Hami-e-bekasan, kya kahega jahan, aapke dar se khali agar jayenge.</i></p>
<p>The full lyrics of Tajdar-e-Haram are among the most loved naats in South Asia — a plea to the King of the Haram for a merciful glance, and a hope that the days of the poor will be set right by his grace.</p>
<h2>Tu Kuja Man Kuja</h2><p><i>Tu kuja man kuja, tu kahan main kahan — you are where, and I am where.</i> A humble naat about the distance between the servant and the beloved Prophet ﷺ, and the longing to close it.</p>
<h2>Hasbi Rabbi Jallallah</h2><p><i>Hasbi Rabbi Jallallah, ma fi qalbi ghayrullah — my Lord suffices me, glory be to Allah, there is nothing in my heart but Allah.</i> A simple, well-known nasheed of reliance on Allah.</p>
<h2>Balaghal Ula Bi Kamalihi</h2><p><i>Balaghal ula bi kamalihi, kashafad duja bi jamalihi, hasunat jami'u khisalihi, sallu alayhi wa aalihi.</i> He reached the highest peak by his perfection, he removed the darkness by his beauty, all his qualities are beautiful — send blessings upon him and his family.</p>
<h2>Maula Ya Salli Wa Sallim</h2><p><i>Maula ya salli wa sallim da'iman abadan, ala habibika khayril khalqi kullihimi.</i> O Master, send blessings and peace always and forever upon Your beloved, the best of all creation.</p>
<p class="notice">Lyrics are shared for reading and learning. Audio and video versions are available from many reciters; search for the naat title on your usual audio platform.</p>"""
    write("naat.html", page("", "Naat Lyrics — Tajdar-e-Haram and More", "Read Naat lyrics: Tajdar-e-Haram, Tu Kuja Man Kuja, Hasbi Rabbi and more.", nb, "naat.html"))

    # WAZAIF
    wb = """<h1>Wazaif</h1><p>Wazaif are regular recitations from the Quran and the Sunnah, done with a sincere intention for a need — for livelihood, health, protection, marriage and peace of heart. A wazifa is not magic: it is dua through the words of Allah, with patience and trust.</p>
<div class="cards">
<div class="card"><h3>Wazifa for Rizq (Livelihood)</h3><p>Recite Surah Al-Waqiah once after Maghrib every evening, and make dua for halal provision. Keep the recitation regular and give charity, even a little, every week.</p></div>
<div class="card"><h3>Wazifa for Shifa (Healing)</h3><p>Recite Surah Al-Fatiha seven times, blow gently on water, and drink it — and continue the treatment your doctor has given you. Healing is from Allah, and medicine is one of His means.</p></div>
<div class="card"><h3>Wazifa for Protection</h3><p>Recite Ayat-ul-Kursi (Quran 2:255) after every prayer, and Surah Al-Ikhlas, Al-Falaq and An-Nas three times in the morning and evening.</p></div>
<div class="card"><h3>Wazifa for Marriage</h3><p>Perform Istikhara first, consult your family, and recite Durood Sharif 100 times daily with the intention of a good, righteous spouse. Haste in marriage often brings regret; patience and counsel are part of the answer.</p></div>
<div class="card"><h3>Wazifa for Peace of Heart</h3><p>Recite "La hawla wa la quwwata illa billah" 100 times a day, and Surah Ar-Rahman with its meaning once a week. The Quran says: "Verily, in the remembrance of Allah do hearts find rest." (13:28)</p></div>
<div class="card"><h3>Wazifa for Forgiveness</h3><p>Recite Astaghfirullah 100 times after Fajr and after Isha, and Sayyid-ul-Istighfar once in the morning and once in the evening. See the <a href="duas.html">Daily Duas</a> page for the full text.</p></div>
</div>
<p class="notice">A wazifa is done with the belief that benefit comes only from Allah. Avoid any practice that asks for money, promises guaranteed results, or adds words that are not from the Quran or authentic Sunnah.</p>"""
    write("wazaif.html", page("", "Wazaif — for Rizq, Shifa, Protection and More", "Islamic wazaif for livelihood, healing, protection, marriage and peace of heart.", wb, "wazaif.html"))

    # 99 NAMES
    nm = """<h1>99 Names of Allah — Asma-ul-Husna</h1><p>The Prophet ﷺ said: "Allah has ninety-nine names; whoever memorises them will enter Paradise." (Sahih al-Bukhari). Below are all 99 names with Arabic, transliteration and meaning.</p>
<input type="search" id="site-search" class="search-box" placeholder="Search a name, e.g. Rahman, Provider..."><p id="search-count"></p>
<div class="cards">"""
    for i, (t, ar, meaning) in enumerate(NAMES99, 1):
        nm += f'<div class="card" data-search="{i} {esc(t)} {esc(meaning)}"><h3>{i}. {esc(t)}</h3><p class="arabic">{esc(ar)}</p><p>{esc(meaning)}</p></div>'
    nm += "</div>"
    write("names.html", page("", "99 Names of Allah with Meaning", "Asma-ul-Husna: all 99 names of Allah with Arabic, transliteration and meaning.", nm, "names.html"))

    # ZAKAT + TASBIH
    zb = """<h1>Zakat Calculator</h1><p>Zakat is 2.5% of your zakatable wealth held for a full lunar year, once it reaches the nisab (the minimum threshold — 85 grams of gold or 595 grams of silver). Enter your amounts below (in your currency).</p>
<form id="zakat-form"><p>Cash in hand and in bank<br><input type="number" id="z-cash" min="0" step="any" placeholder="0"></p>
<p>Gold (current value)<br><input type="number" id="z-gold" min="0" step="any" placeholder="0"></p>
<p>Silver (current value)<br><input type="number" id="z-silver" min="0" step="any" placeholder="0"></p>
<p>Investments and business stock (current value)<br><input type="number" id="z-inv" min="0" step="any" placeholder="0"></p>
<p>Debts you owe (deduct)<br><input type="number" id="z-debt" min="0" step="any" placeholder="0"></p>
<p>Nisab (optional — enter the value of 85g gold in your currency; leave blank to skip the nisab check)<br><input type="number" id="z-nisab" min="0" step="any" placeholder="0"></p>
<p><button class="btn" type="submit" style="border:0;cursor:pointer">Calculate Zakat</button></p></form>
<div id="zakat-result" class="card"></div>"""
    write("zakat.html", page("", "Zakat Calculator", "Calculate 2.5% Zakat on cash, gold, silver and investments.", zb, "zakat.html"))

    tb = """<h1>Digital Tasbih</h1><p>Tap the circle to count your dhikr. Set a target and the counter will restart with a message when you reach it.</p>
<p>Target: <select id="tasbih-target"><option value="33">33</option><option value="100">100</option><option value="500">500</option><option value="1000">1000</option></select></p>
<div class="tasbih-big"><span id="tasbih-count">0</span></div>
<p style="text-align:center">Total this session: <span id="tasbih-total">0</span></p>
<button class="tasbih-btn" id="tasbih-tap">Tap to Count<br><small>SubhanAllah • Alhamdulillah • Allahu Akbar</small></button>
<p style="text-align:center"><button id="tasbih-reset">Reset</button></p>
<p>The Prophet ﷺ taught that saying SubhanAllah, Alhamdulillah and Allahu Akbar 33 times each after prayer is a source of great reward.</p>"""
    write("tasbih.html", page("", "Digital Tasbih Counter", "Free digital Tasbih counter for dhikr with targets of 33, 100, 500 or 1000.", tb, "tasbih.html"))

    # ABOUT / CONTACT / DONATE / PRIVACY / CLASSES
    write("about.html", page("", "About Faiz e Islam", "About Faiz e Islam — authentic Quran, Durood, Duas, Surahs and Islamic knowledge, free for everyone.",
    """<h1>About Faiz e Islam</h1><p>Faiz e Islam is a free Islamic learning platform. We aim to make the Quran, Durood, Duas, Kalimas and Salaat easy to read, listen to and understand — with Urdu and English translation, audio recitation and clear guides.</p>
<h2>What we offer</h2><ul><li>The complete Holy Quran — all 114 Surahs with translation and audio.</li><li>Durood, the six Kalimas, and more than 20 daily duas.</li><li>Step-by-step guides to Salaat and Istikhara.</li><li>Islamic blogs, Naat lyrics and Wazaif.</li><li>Online Quran classes for children and adults.</li></ul>
<h2>Our promise</h2><p>All resources on this site are free, with no subscription and no paywall. Running the platform has costs — hosting, domain and the time of our team — so donations are welcome, but they are never required to read or listen.</p>
<p>Quran text and translations on this site are provided by <a href="https://alquran.cloud/">AlQuran.cloud</a>, and audio by the Islamic Network CDN. The Arabic of the Quran and the text of hadith are kept as they are; our own introductions, guides and answers are written freshly for this site.</p>""", "about.html"))

    write("contact.html", page("", "Contact Us", "Contact Faiz e Islam.",
    """<h1>Contact Us</h1><p>If you have a question, a correction, or a suggestion for the site, we would love to hear from you. Use the form below — it opens your email app with your message addressed to us.</p>
<form action="mailto:info@faizeislam.example" method="post" enctype="text/plain">
<p>Your name<br><input type="text" name="name" required></p>
<p>Your email<br><input type="email" name="email" required></p>
<p>Message<br><textarea name="message" rows="6" required></textarea></p>
<p><button class="btn" type="submit" style="border:0;cursor:pointer">Send Message</button></p></form>
<p class="notice">Email address: info@faizeislam.example — this is the address used on this new site; it will be replaced with the owner's real address before launch.</p>""", "contact.html"))

    write("donate.html", page("", "Donate — Support Faiz e Islam", "Donate to support Faiz e Islam.",
    """<h1>Donate — Support Faiz e Islam</h1><p>All resources on this site are free. Your donation helps pay for hosting, the domain and the work of preparing new content — and it is Sadaqah Jariyah, ongoing charity that continues to benefit others.</p>
<h2>How your donation is used</h2><ul><li>Hosting and domain for the website.</li><li>Preparing new Surah pages, guides and blog articles.</li><li>Supporting online Quran classes for students who cannot afford them.</li></ul>
<p class="notice"><b>Payment method:</b> no payment method is set up yet. The site owner will add the donation method (bank transfer or another option of their choice) before launch. Until then, please use the <a href="contact.html">contact page</a> if you would like to support the project.</p>""", "donate.html"))

    write("privacy-policy.html", page("", "Privacy Policy", "Privacy Policy of Faiz e Islam.",
    """<h1>Privacy Policy</h1><p>This website does not require an account, and we do not sell or share personal information.</p>
<h2>What we collect</h2><p>We do not collect names, emails or locations through this site. If you email us through the contact page, we receive only what you choose to send, and we use it only to reply to you.</p>
<h2>Cookies and third parties</h2><p>Quran audio is streamed from the Islamic Network CDN and Quran text from AlQuran.cloud. Those services may log the Surah or audio file requested, as any web server does. We do not run advertising or tracking of our own.</p>
<h2>Changes</h2><p>If this policy changes, the updated version will be published on this page.</p>""", "privacy-policy.html"))

    write("quran-classes.html", page("", "Online Quran Classes", "Learn Quran online with a teacher — Noorani Qaida, Nazra, Hifz and Tajweed.",
    """<h1>Online Quran Classes</h1><p>Learn the Quran online, one-to-one, with a qualified teacher — for children and adults, from anywhere in the world.</p>
<div class="cards">
<div class="card"><h3>Noorani Qaida</h3><p>For beginners: the Arabic alphabet, joining letters, and the first steps of reading.</p></div>
<div class="card"><h3>Nazra (Quran Reading)</h3><p>Fluent reading of the Holy Quran with correct pronunciation.</p></div>
<div class="card"><h3>Tajweed</h3><p>The rules of beautiful, correct recitation, with practice and correction.</p></div>
<div class="card"><h3>Hifz (Memorisation)</h3><p>A structured plan to memorise the Quran, with daily revision and a teacher's guidance.</p></div>
<div class="card"><h3>Namaz Training</h3><p>Learning prayer, its duas and its meaning — for children and new Muslims.</p></div>
<div class="card"><h3>Islamic Studies</h3><p>Basic beliefs (Aqaid), daily duas and Islamic manners for children.</p></div>
</div>
<h2>How to enrol</h2><p>Classes are held online at a time that suits you. To enrol, or to book a free trial lesson, please use the <a href="contact.html">contact page</a> and tell us the student's age, level and preferred timings. Fees and timings will be confirmed by the site owner before launch.</p>""", "quran-classes.html"))

# ---------- Surah pages (Template A) ----------
FATIHA_AR = ["بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ","ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ","ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ","مَـٰلِكِ يَوْمِ ٱلدِّينِ","إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ","ٱهْدِنَا ٱلصِّرَ ٰ⁠طَ ٱلْمُسْتَقِيمَ","صِرَ ٰ⁠طَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّاۤلِّينَ"]
FATIHA_UR = ["شروع کرتا ہوں اللہ تعالیٰ کے نام سے جو بڑا مہربان نہایت رحم والا ہے","سب تعریف اللہ تعالیٰ کے لئے ہے جو تمام جہانوں کا پالنے والا ہے","بڑا مہربان نہایت رحم کرنے والا","بدلے کے دن (یعنی قیامت) کا مالک ہے","ہم صرف تیری ہی عبادت کرتے ہیں اور صرف تجھ ہی سے مدد چاہتے ہیں","ہمیں سیدھی (اور سچی) راہ دکھا","ان لوگوں کی راہ جن پر تو نے انعام کیا ان کی نہیں جن پر غضب کیا گیا اور نہ گمراہوں کی"]
FATIHA_EN = ["In the name of Allah, the Entirely Merciful, the Especially Merciful.","[All] praise is [due] to Allah, Lord of the worlds —","The Entirely Merciful, the Especially Merciful,","Sovereign of the Day of Recompense.","It is You we worship and You we ask for help.","Guide us to the straight path —","The path of those upon whom You have bestowed favor, not of those who have evoked [Your] anger or of those who are astray."]
FATIHA_OVERVIEW = "Surah Al-Fatiha is the first Surah of the Holy Quran and the one every Muslim recites in every rak'ah of every prayer. It has only seven verses, yet it holds the whole message of the Quran in brief: who Allah is, why we worship Him alone, and the one prayer every believer keeps asking — guide us to the straight path. That is why it is also called Umm al-Kitab, the Mother of the Book. On this page you can read it verse by verse with Urdu and English translation, listen to the recitation, and download it as a PDF."
FATIHA_VIRTUES = [
 "No prayer is complete without it — the Prophet ﷺ taught that the prayer of a person who does not recite Al-Fatiha is not complete, which is why it is read in every rak'ah.",
 "It is a conversation with Allah: each verse is answered, so reciting it slowly, pausing after each verse, turns the prayer into a dialogue rather than a rush.",
 "It is also a cure and a protection — Muslims have recited it for healing and for safety since the earliest days, and it is the first thing many parents teach their children.",
]
FATIHA_FAQS = [
 ("How many verses are in Surah Al-Fatiha?","Seven verses. It is the shortest complete Surah by count after the very short ones, and the first Surah of the Quran."),
 ("Is Surah Al-Fatiha Makki or Madani?","Makki — it was revealed in Makkah, before the Hijrah."),
 ("Can I read Surah Al-Fatiha without wudu?","You can recite it from memory without wudu, but touching the printed Quran (mushaf) requires wudu. The same rule applies on this site: reading on screen is fine."),
 ("Why is it called Umm al-Kitab?","Because it contains the essence of the whole Quran — praise of Allah, worship of Him alone, and the prayer for guidance — in just seven verses."),
 ("Which para (Juz) is Surah Al-Fatiha in?","Para 1, at the very beginning of the Quran."),
]

def ordinal(n):
    if 10 <= n % 100 <= 20: s = "th"
    else: s = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{s}"

def surah_overview(name, n, rev, count, meaning, para):
    place = "Makkah, before the Hijrah" if rev == "Meccan" else "Madinah, after the Hijrah"
    revw = "Makki" if rev == "Meccan" else "Madani"
    if count <= 10:
        length = "one of the short Surahs of the Quran, often among the first that children memorise"
    elif count <= 50:
        length = "a Surah of moderate length, easy to read in one sitting"
    else:
        length = "one of the longer Surahs of the Quran, to be read in parts over several sittings"
    return (f"Surah {name} is the {ordinal(n)} Surah of the Holy Quran. It was revealed in {place}, "
            f"which makes it a {revw} Surah, and it has {count} verses. Its name means \u201c{meaning}\u201d. "
            f"It is {length}. On this page you can read it verse by verse with Urdu and English translation, "
            f"listen to the recitation by Mishary Rashid Alafasy, and reflect on its message. The Surah begins in Para {para}.")

def surah_virtues(name, count):
    return [
     f"Reading Surah {name} is reading the words of Allah — every letter brings reward, and reading with its meaning brings understanding with it.",
     f"Make it part of your daily routine: a few verses each day, with their Urdu or English translation, is better than rushing through many pages without understanding.",
     f"Teach it to your children and share it with your family — the Quran is meant to be read, understood and lived by, not only kept on a shelf.",
    ]

def surah_faqs(name, n, rev, count, para, meaning):
    revw = "Makki" if rev == "Meccan" else "Madani"
    return [
     (f"How many verses are in Surah {name}?", f"Surah {name} has {count} verses."),
     (f"Is Surah {name} Makki or Madani?", f"{revw} — it was revealed in {'Makkah' if rev=='Meccan' else 'Madinah'}."),
     (f"What does the name {name} mean?", f"It means \u201c{meaning}\u201d."),
     (f"Which para (Juz) does Surah {name} begin in?", f"Para {para}."),
     (f"Where can I listen to Surah {name}?", "Use the audio player at the top of this page — recitation by Mishary Rashid Alafasy."),
    ]

def build_surahs():
    meta = []
    failed = []
    for n in range(1, 115):
        slug = SLUGS[n - 1]
        try:
            ar, ur, en = get_surah(n)
        except Exception as e:
            print(f"FAILED surah {n}: {e}"); failed.append(n); continue
        name = ar["englishName"]
        meaning = ar.get("englishNameTranslation") or name
        rev = ar["revelationType"]
        count = ar["numberOfAyahs"]
        para = ar["ayahs"][0].get("juz", 1)
        meta.append({"n": n, "slug": slug, "name": name, "meaning": meaning, "rev": rev, "count": count, "para": para})
        if n == 1:
            ar_texts, ur_texts, en_texts = FATIHA_AR, FATIHA_UR, FATIHA_EN
            overview, virtues, faqs = FATIHA_OVERVIEW, FATIHA_VIRTUES, FATIHA_FAQS
        else:
            ar_texts = [a["text"].strip() for a in ar["ayahs"]]
            ur_texts = [a["text"].strip() for a in ur["ayahs"]]
            en_texts = [a["text"].strip() for a in en["ayahs"]]
            overview = surah_overview(name, n, rev, count, meaning, para)
            virtues = surah_virtues(name, count)
            faqs = surah_faqs(name, n, rev, count, para, meaning)
        verses = ""
        for i, (a, u, e) in enumerate(zip(ar_texts, ur_texts, en_texts), 1):
            verses += (f'<div class="ayah"><p><span class="num">Ayah {i}</span></p>'
                       f'<p class="arabic">{esc(a)}</p><p class="urdu">{esc(u)}</p>'
                       f'<p><b>English:</b> {esc(e)}</p></div>')
        prev_link = f'<a href="surah-{SLUGS[n-2]}.html">&larr; Previous Surah</a>' if n > 1 else "—"
        next_link = f'<a href="surah-{SLUGS[n]}.html">Next Surah &rarr;</a>' if n < 114 else "—"
        faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)
        body = f"""<p class="breadcrumb"><a href="../al-quran.html">Al Quran</a> &raquo; Surah {name}</p>
<h1>Surah {esc(name)} — {esc(meaning)}</h1>
<div class="facts"><span>Surah {n} of 114</span><span>{count} Ayahs</span><span>{'Makki' if rev=='Meccan' else 'Madani'}</span><span>Para {para}</span><span>Also known as: {esc(name)}</span></div>
<p>{esc(overview)}</p>
<div class="audio-box"><h2>Listen Online</h2><p>Qari: Mishary Rashid Alafasy. Source: Islamic Network CDN via AlQuran.cloud.</p>
<audio controls preload="none" src="https://cdn.islamic.network/quran/audio/128/ar.alafasy/{n}.mp3"></audio>
<p><a href="https://cdn.islamic.network/quran/audio/128/ar.alafasy/{n}.mp3">Download audio (MP3)</a></p></div>
<h2>Full text — Arabic, Urdu, English (verse by verse)</h2>{verses}
<h2>Virtues and benefits</h2><ul>{''.join(f'<li>{esc(v)}</li>' for v in virtues)}</ul>
<h2>Frequently Asked Questions</h2><div class="faq">{faq_html}</div>
<p>{prev_link} &nbsp;|&nbsp; {next_link} &nbsp;|&nbsp; <a href="../al-quran.html">All 114 Surahs</a></p>
<p class="notice">Quran Arabic text, Urdu translation (Junagarhi) and English translation (Sahih International): <a href="https://alquran.cloud/">AlQuran.cloud</a>. Audio: Islamic Network CDN.</p>"""
        write(f"al-quran/surah-{slug}.html",
              page("../", f"Surah {name} — Read and Listen Online",
                   f"Read Surah {name} with Arabic, Urdu and English translation and audio.",
                   body, "al-quran.html"))
        if n % 20 == 0:
            print(f"  ... {n}/114 surahs done")
    return meta, failed

def build_quran_list(meta):
    items = "".join(
        f'<a href="al-quran/surah-{m["slug"]}.html" data-search="{m["n"]} {esc(m["name"])} {esc(m["meaning"])} surah"><span class="n">{m["n"]}</span> Surah {esc(m["name"])} <small>— {esc(m["meaning"])} · {m["count"]} Ayahs · {"Makki" if m["rev"]=="Meccan" else "Madani"}</small></a>'
        for m in meta)
    popular = ["al-fatiha","yaseen","ar-rahman","al-mulk","al-kahf","al-waqiah","maryam","yusuf"]
    pop = "".join(f'<div class="card"><h3>Surah {s.replace("-"," ").title()}</h3><p><a href="al-quran/surah-{s}.html">Read Surah &rarr;</a></p></div>' for s in popular)
    body = f"""<h1>Al Quran</h1><p>Read and listen to all 114 Surahs of the Holy Quran with Arabic text, Urdu and English translation, and audio recitation.</p>
<h2>Most Read Surahs</h2><div class="cards">{pop}</div>
<h2>Read &amp; Listen to all 114 Surahs</h2>
<input type="search" id="site-search" class="search-box" placeholder="Search by Surah name or number, e.g. Rahman or 55"><p id="search-count"></p>
<div class="surah-list">{items}</div>
<h2>Understanding the Holy Quran</h2><p>The Quran has 114 Surahs and 30 Paras (Juz). Surahs revealed in Makkah are called Makki and those revealed in Madinah are called Madani. Read it with Tajweed, slowly, and with its meaning — a little each day is better than a lot in a hurry.</p>"""
    write("al-quran.html", page("", "Al Quran — Read 114 Surahs Online", "Read all 114 Surahs of the Holy Quran with Arabic, Urdu and English translation and audio.", body, "al-quran.html"))

def main():
    write("assets/css/style.css", CSS)
    write("assets/js/main.js", JS)
    write("vercel.json", json.dumps({"cleanUrls": True, "trailingSlash": False}, indent=2) + "\n")
    static_pages()
    meta, failed = build_surahs()
    build_quran_list(meta)
    readme = """# Faiz e Islam — Website (coded, multi-page, static)

A complete multi-page static website in plain HTML + CSS + JavaScript — **not WordPress, not a single-page demo**. Every section is its own page, and every one of the 114 Surahs has its own page under `al-quran/`.

## Structure

- `index.html` — Home (hero, Quran, Durood, Most Read Surahs, Kalimas, Salaat, Duas, Istikhara, Blogs, tools)
- `al-quran.html` — searchable list of all 114 Surahs
- `al-quran/surah-<slug>.html` — one page per Surah (114 pages, Template A: facts, audio, Arabic + Urdu + English verse by verse, virtues, FAQs)
- `durood.html`, `kalimas.html`, `salaat.html`, `duas.html`, `istikhara.html`, `blogs.html`, `naat.html`, `wazaif.html`, `names.html` (99 Names), `zakat.html`, `tasbih.html`, `about.html`, `contact.html`, `donate.html`, `privacy-policy.html`, `quran-classes.html`
- `blogs/*.html` — 6 blog articles
- `assets/css/style.css`, `assets/js/main.js` — shared theme and tools (nav, search, Tasbih, Zakat calculator)
- `vercel.json` — clean URLs (no `.html` needed)

## Data sources

Quran Arabic text and Urdu (Junagarhi) / English (Sahih International) translations: **AlQuran.cloud** API. Audio: Mishary Rashid Alafasy via the **Islamic Network CDN**. Introductions, guides, virtues and FAQs are written freshly for this site — the Quran text and translations are kept as-is with source credit, as in the structure document.

## Run locally

```bash
cd faiz-e-islam-site
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy on Vercel (complete testing)

1. Push this folder to a GitHub repository, or run `vercel` in this folder.
2. In Vercel, choose **Import Project** and select the repository.
3. Framework preset: **Other** (static site). **Build command: leave empty. Output directory: leave as the project root (`.`).**
4. Click **Deploy**. Vercel serves the static files; `vercel.json` gives clean URLs, so `/al-quran` works without `.html`.
5. Test the live site, then add your own domain in Vercel under **Settings → Domains** when you buy one.

No build step, no database, no server code is needed.
"""
    write("README.md", readme)
    print(f"\nDONE: {len(meta)} surah pages, failed: {failed}")
    total = sum(len(files) for _, _, files in os.walk(ROOT))
    print(f"Total files in site: {total}")
    for rel in sorted(os.listdir(ROOT)):
        print(" ", rel)

if __name__ == "__main__":
    main()
