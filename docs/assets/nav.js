// Shared navigation component for all pages
(function() {
  const pages = [
    { href: 'index.html', label: 'Dashboard', icon: '📊' },
    { href: 'trends.html', label: 'Trends', icon: '📈' },
    { href: 'attrition.html', label: 'Class 9 Cliff', icon: '🪜' },
    { href: 'infrastructure.html', label: 'Infrastructure', icon: '🏗️' },
    { href: 'teachers.html', label: 'Teachers', icon: '👩‍🏫' },
    { href: 'success.html', label: 'Success Stories', icon: '🏆' },
    { href: 'scorecard.html', label: 'Scorecard', icon: '📋' },
    { href: 'story.html', label: 'Data Story', icon: '📖' },
  ];

  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  const nav = document.createElement('nav');
  nav.className = 'topnav';
  nav.setAttribute('role', 'navigation');
  nav.setAttribute('aria-label', 'Main navigation');

  const inner = document.createElement('div');
  inner.className = 'topnav-inner';

  // Brand
  const brand = document.createElement('div');
  brand.className = 'topnav-brand';
  brand.innerHTML = `
    <div class="flag"><span class="s"></span><span class="w"></span><span class="g"></span></div>
    UDISE+ · Girls' Dropout Analysis
  `;

  // Links
  const links = document.createElement('div');
  links.className = 'topnav-links';

  pages.forEach(p => {
    const a = document.createElement('a');
    a.href = p.href;
    a.textContent = p.label;
    if (currentPage === p.href || (currentPage === '' && p.href === 'index.html')) {
      a.className = 'active';
    }
    links.appendChild(a);
  });

  inner.appendChild(brand);
  inner.appendChild(links);
  nav.appendChild(inner);

  // Insert at top of body
  document.body.insertBefore(nav, document.body.firstChild);
})();
