#!/usr/bin/env python3
"""Ashward yasal sayfalar — markdown -> HTML üretici.

Kullanım (ashward-legal kökünden):
    pip install markdown
    python tools/build.py [--source PATH]

Ne yapar:
    - privacy_en.md / privacy_tr.md / terms_en.md / terms_tr.md dosyalarını
      Ashward uygulama deposundan (TEK doğru kaynak — buraya elle metin
      kopyalanmaz) okur, Python `markdown` paketiyle HTML'e çevirir.
    - index.html ve support.html içeriğini de (nav/dil değiştirici/şablon
      tutarlılığı için) bu script üretir.
    - Hepsini style.css'i kullanan ortak bir şablonla sarıp bu klasöre
      (ashward-legal/) yazar.

Kaynak varsayılan konumu: bu depoyle KARDEŞ dizindeki ashward deposu
    ../ashward/assets/policies/
Farklı bir konumdaysa: python tools/build.py --source "C:/yol/assets/policies"
"""
import argparse
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("markdown paketi kurulu değil. Önce: pip install markdown", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT.parent / "ashward" / "assets" / "policies"

SITE_URL = "https://studio-releaf.github.io/ashward-legal"
CONTACT_EMAIL = "ataseversoftware@gmail.com"

# Uygulama kodundan (bkz. lib/l10n/app_en.arb / app_tr.arb) alınan GERÇEK
# metinler — buradan uydurulmadı:
HEALTH_DISCLAIMER_EN = (
    "Ashward is not a medical device and does not provide medical advice. "
    "Health information is general, based on public sources, and timings "
    "vary from person to person. For medical advice, consult a healthcare "
    "professional."
)
HEALTH_DISCLAIMER_TR = (
    "Ashward tıbbi bir cihaz değildir ve tıbbi tavsiye vermez. Sağlık "
    "bilgileri geneldir, kamuya açık kaynaklara dayanır ve süreler kişiden "
    "kişiye değişir. Tıbbi tavsiye için bir sağlık uzmanına danış."
)
DELETE_ACCOUNT_PATH_EN = "Profile &amp; Settings → Security &amp; Account → Delete Account"
DELETE_ACCOUNT_PATH_TR = "Profil &amp; Ayarlar → Güvenlik ve Hesap → Hesabı Sil"
RESTORE_BUTTON_EN = "Restore Previous Purchases"
RESTORE_BUTTON_TR = "Önceki Satın Alımları Geri Yükle"


def render_markdown(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=["tables", "sane_lists"])


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical_href}">
<link rel="stylesheet" href="{css_href}">
</head>
<body>
<div class="wrap">
  <header class="site">
    <a class="wordmark" href="{home_href}"><span class="ash">Ash</span><span class="ward">ward</span></a>
    <nav class="site">
      <a href="{privacy_href}"{privacy_active}>Privacy</a>
      <a href="{terms_href}"{terms_active}>Terms</a>
      <a href="{support_href}"{support_active}>Support</a>
    </nav>
  </header>
{lang_switch}
  <main>
{body}
  </main>
  <footer class="site">
    <p>Ashward &middot; <a href="mailto:{email}">{email}</a></p>
  </footer>
</div>
</body>
</html>
"""


def lang_switch_html(active: str, en_href: str, tr_href: str) -> str:
    if active is None:
        return ""
    en_cls = " class=\"active\"" if active == "en" else ""
    tr_cls = " class=\"active\"" if active == "tr" else ""
    return (
        f'  <p class="lang-switch">Language:'
        f' <a href="{en_href}"{en_cls}>EN</a>'
        f' <a href="{tr_href}"{tr_cls}>TR</a></p>\n'
    )


def write_page(
    filename: str,
    *,
    html_lang: str,
    title: str,
    description: str,
    body: str,
    nav_active: str,
    lang_switch: str = "",
    depth: int = 0,
) -> None:
    prefix = "" if depth == 0 else "../" * depth
    html = PAGE_TEMPLATE.format(
        html_lang=html_lang,
        title=title,
        description=description,
        canonical_href=f"{SITE_URL}/{filename}",
        css_href=f"{prefix}style.css",
        home_href=f"{prefix}index.html",
        privacy_href=f"{prefix}privacy.html",
        privacy_active=' class="active"' if nav_active == "privacy" else "",
        terms_href=f"{prefix}terms.html",
        terms_active=' class="active"' if nav_active == "terms" else "",
        support_href=f"{prefix}support.html",
        support_active=' class="active"' if nav_active == "support" else "",
        lang_switch=lang_switch,
        body=body,
        email=CONTACT_EMAIL,
    )
    out = ROOT / filename
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"  yazıldı: {out.relative_to(ROOT)}")


def build_policy_page(
    md_name: str,
    out_name: str,
    *,
    lang: str,
    title: str,
    description: str,
    nav_active: str,
    en_href: str,
    tr_href: str,
    source: Path,
) -> None:
    md_path = source / md_name
    if not md_path.exists():
        print(f"HATA: kaynak bulunamadı: {md_path}", file=sys.stderr)
        sys.exit(1)
    body_html = render_markdown(md_path)
    switch = lang_switch_html(lang, en_href, tr_href)
    write_page(
        out_name,
        html_lang=lang,
        title=title,
        description=description,
        body=body_html,
        nav_active=nav_active,
        lang_switch=switch,
    )


def build_index() -> None:
    body = """    <div class="hero">
      <span class="wordmark"><span class="ash">Ash</span><span class="ward">ward</span></span>
      <p>Ashward is a quit-smoking companion app for iPhone. This page hosts
      the legal and support pages required by the App Store — the app
      itself is not distributed from here.</p>
    </div>
    <div class="link-grid">
      <a class="link-card" href="privacy.html">
        <div class="title">Privacy Policy</div>
        <div class="desc">English</div>
      </a>
      <a class="link-card" href="privacy-tr.html">
        <div class="title">Gizlilik Politikası</div>
        <div class="desc">Türkçe</div>
      </a>
      <a class="link-card" href="terms.html">
        <div class="title">Terms of Service</div>
        <div class="desc">English</div>
      </a>
      <a class="link-card" href="terms-tr.html">
        <div class="title">Kullanım Şartları</div>
        <div class="desc">Türkçe</div>
      </a>
      <a class="link-card" href="support.html">
        <div class="title">Support</div>
        <div class="desc">Contact &amp; FAQ &middot; EN/TR</div>
      </a>
    </div>
"""
    write_page(
        "index.html",
        html_lang="en",
        title="Ashward — Legal &amp; Support",
        description="Ashward privacy policy, terms of service, and support information.",
        body=body,
        nav_active="",
    )


def build_support() -> None:
    body = f"""    <h1>Support</h1>
    <p class="subtitle">Ashward &middot; Destek / Support &middot; EN &amp; TR</p>

    <h2>Contact &middot; İletişim</h2>
    <p>
      <strong>Email:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>
      We aim to respond within 30 days. &middot; 30 gün içinde yanıt vermeyi hedefliyoruz.
    </p>

    <h2>FAQ &middot; Sık Sorulan Sorular</h2>

    <div class="faq-item">
      <p class="q"><span class="badge en">EN</span>How do I delete my account?</p>
      <p>In the app: <strong>{DELETE_ACCOUNT_PATH_EN}</strong>. Confirm the
      deletion. Alternatively, email us at
      <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with the subject
      &ldquo;Account Deletion Request.&rdquo;</p>
    </div>
    <div class="faq-item">
      <p class="q"><span class="badge tr">TR</span>Hesabımı nasıl silerim?</p>
      <p>Uygulama içinde: <strong>{DELETE_ACCOUNT_PATH_TR}</strong>. Silme
      işlemini onaylayın. Alternatif olarak
      <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> adresine &ldquo;Hesap
      Silme Talebi&rdquo; konulu bir e-posta gönderebilirsiniz.</p>
    </div>

    <div class="faq-item">
      <p class="q"><span class="badge en">EN</span>How do I restore my purchase?</p>
      <p>Open the paywall in the app and tap <strong>&ldquo;{RESTORE_BUTTON_EN}&rdquo;</strong>.
      This restores your lifetime purchase to your current account.</p>
    </div>
    <div class="faq-item">
      <p class="q"><span class="badge tr">TR</span>Satın alımımı nasıl geri yüklerim?</p>
      <p>Uygulamada premium ekranını (paywall) açın ve
      <strong>&ldquo;{RESTORE_BUTTON_TR}&rdquo;</strong> düğmesine dokunun. Bu,
      ömür boyu satın alımınızı mevcut hesabınıza geri yükler.</p>
    </div>

    <div class="faq-item">
      <p class="q"><span class="badge en">EN</span>I'm not receiving notifications</p>
      <p>Check that notifications are enabled for Ashward: on your iPhone,
      go to <strong>Settings → Notifications → Ashward</strong> and make sure
      &ldquo;Allow Notifications&rdquo; is on.</p>
    </div>
    <div class="faq-item">
      <p class="q"><span class="badge tr">TR</span>Bildirimler gelmiyor</p>
      <p>Ashward için bildirimlerin açık olduğunu kontrol edin: iPhone'unuzda
      <strong>Ayarlar → Bildirimler → Ashward</strong> yolunu izleyin ve
      &ldquo;Bildirimlere İzin Ver&rdquo; seçeneğinin açık olduğundan emin olun.</p>
    </div>

    <div class="faq-item">
      <p class="q"><span class="badge en">EN</span>Is Ashward a medical product?</p>
      <p>{HEALTH_DISCLAIMER_EN}</p>
    </div>
    <div class="faq-item">
      <p class="q"><span class="badge tr">TR</span>Ashward tıbbi bir ürün mü?</p>
      <p>{HEALTH_DISCLAIMER_TR}</p>
    </div>

    <h2>Legal &middot; Yasal</h2>
    <p>
      <a href="privacy.html">Privacy Policy</a> &middot;
      <a href="privacy-tr.html">Gizlilik Politikası</a> &middot;
      <a href="terms.html">Terms of Service</a> &middot;
      <a href="terms-tr.html">Kullanım Şartları</a>
    </p>
"""
    write_page(
        "support.html",
        html_lang="en",
        title="Ashward — Support",
        description="Ashward support: contact email and frequently asked questions (EN/TR).",
        body=body,
        nav_active="support",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    args = ap.parse_args()
    source = Path(args.source)

    print(f"Kaynak: {source}")
    if not source.exists():
        print(f"HATA: kaynak klasör yok: {source}", file=sys.stderr)
        print(
            "İpucu: --source ile assets/policies klasörünün tam yolunu verin.",
            file=sys.stderr,
        )
        sys.exit(1)

    build_policy_page(
        "privacy_en.md",
        "privacy.html",
        lang="en",
        title="Ashward — Privacy Policy",
        description="Ashward Privacy Policy (English).",
        nav_active="privacy",
        en_href="privacy.html",
        tr_href="privacy-tr.html",
        source=source,
    )
    build_policy_page(
        "privacy_tr.md",
        "privacy-tr.html",
        lang="tr",
        title="Ashward — Gizlilik Politikası",
        description="Ashward Gizlilik Politikası (Türkçe).",
        nav_active="privacy",
        en_href="privacy.html",
        tr_href="privacy-tr.html",
        source=source,
    )
    build_policy_page(
        "terms_en.md",
        "terms.html",
        lang="en",
        title="Ashward — Terms of Service",
        description="Ashward Terms of Service (English).",
        nav_active="terms",
        en_href="terms.html",
        tr_href="terms-tr.html",
        source=source,
    )
    build_policy_page(
        "terms_tr.md",
        "terms-tr.html",
        lang="tr",
        title="Ashward — Kullanım Şartları",
        description="Ashward Kullanım Şartları (Türkçe).",
        nav_active="terms",
        en_href="terms.html",
        tr_href="terms-tr.html",
        source=source,
    )
    build_index()
    build_support()
    print("Bitti.")


if __name__ == "__main__":
    main()
