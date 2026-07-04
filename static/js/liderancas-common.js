/**
 * Lideranças — Funções compartilhadas
 * Máscara de telefone + carregamento dinâmico de cidades por região
 */

(function () {
    'use strict';

    // ===== Máscara de telefone =====
    function initPhoneMask(selector) {
        const el = document.querySelector(selector || '#id_telefone');
        if (!el) return;
        el.addEventListener('input', function (e) {
            let v = e.target.value.replace(/\D/g, '');
            if (v.length > 11) v = v.slice(0, 11);
            if (v.length <= 2) v = v.replace(/^(\d{0,2})/, '($1');
            else if (v.length <= 6) v = v.replace(/^(\d{2})(\d{0,4})/, '($1) $2');
            else if (v.length <= 10) v = v.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            else v = v.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
            e.target.value = v;
        });
    }

    // ===== Carregamento de cidades por região =====
    function initCityLoader(regiaoSelector, cidadeSelector, keepCurrent) {
        const regiao = document.querySelector(regiaoSelector || '#id_regiao');
        const cidade = document.querySelector(cidadeSelector || '#id_cidade');
        if (!regiao || !cidade) return;

        const cidadeAtual = cidade.value;

        regiao.addEventListener('change', function () {
            const regiaoId = regiao.value;
            cidade.innerHTML = '<option value="">---------</option>';
            if (!regiaoId) return;

            fetch('/liderancas/api/cidades/' + regiaoId + '/')
                .then(function (r) { return r.json(); })
                .then(function (cidades) {
                    cidades.forEach(function (c) {
                        var opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = c.nome;
                        if (keepCurrent && String(c.id) === String(cidadeAtual)) {
                            opt.selected = true;
                        }
                        cidade.appendChild(opt);
                    });
                });
        });
    }

    // ===== Carregamento de cidades nos filtros =====
    function initFilterCityLoader(regiaoSelector, cidadeSelector) {
        const regiao = document.querySelector(regiaoSelector || '#filtroRegiao');
        const cidade = document.querySelector(cidadeSelector || '#filtroCidade');
        if (!regiao || !cidade) return;

        regiao.addEventListener('change', function () {
            var regiaoId = regiao.value;
            cidade.innerHTML = '<option value="">Todas</option>';
            if (!regiaoId) return;

            fetch('/liderancas/api/cidades/' + regiaoId + '/')
                .then(function (r) { return r.json(); })
                .then(function (cidades) {
                    cidades.forEach(function (c) {
                        var opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = c.nome;
                        cidade.appendChild(opt);
                    });
                });
        });
    }

    // ===== Dropdown customizado de região com preview de cidades no hover =====
    // O <select> nativo do macOS não exibe tooltip nas opções, então trocamos o select
    // de região por um dropdown próprio: cada linha carrega data-tip (o balão #ajTip já
    // existente em base.html) com as cidades da região. O <select> nativo permanece no
    // DOM (escondido) como fonte de verdade — sincronizamos o valor e disparamos 'change'
    // para não quebrar o carregamento de cidades/coordenadores que já existe.
    var _regioesCidadesPromise = null;
    function _fetchRegioesCidades() {
        if (!_regioesCidadesPromise) {
            _regioesCidadesPromise = fetch('/liderancas/api/regioes-cidades/')
                .then(function (r) { return r.json(); })
                .catch(function () { return {}; });  // offline/erro: dropdown sem preview, sem quebrar
        }
        return _regioesCidadesPromise;
    }

    var CARET = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E";
    function _injectRcdCss() {
        if (document.getElementById('rcd-css')) return;
        var st = document.createElement('style');
        st.id = 'rcd-css';
        st.textContent =
            '.rcd{position:relative;width:100%;}' +
            '.rcd-btn{display:flex;align-items:center;width:100%;text-align:left;padding-right:34px;' +
            'position:relative;box-sizing:border-box;}' +
            ".rcd-btn::after{content:'';position:absolute;right:12px;top:50%;width:12px;height:12px;" +
            'margin-top:-6px;pointer-events:none;background:url("' + CARET + '") no-repeat center;}' +
            '.rcd-btn:focus{outline:none;border-color:var(--accent);background:#fff;box-shadow:0 0 0 3px var(--accent-ring);}' +
            '.rcd-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;width:100%;}' +
            '.rcd-label.rcd-placeholder{color:#94a3b8;}' +
            '.rcd-list{position:absolute;z-index:900;top:calc(100% + 4px);left:0;right:0;max-height:320px;' +
            'overflow-y:auto;background:#fff;border:1.5px solid #e2e8f0;border-radius:12px;' +
            'box-shadow:0 12px 30px rgba(0,0,0,.14);padding:4px;display:none;}' +
            '.rcd.open .rcd-list{display:block;}' +
            '.rcd-opt{padding:8px 12px;border-radius:8px;font-size:0.85rem;color:#1e293b;cursor:pointer;line-height:1.35;}' +
            '.rcd-opt:hover,.rcd-opt.active{background:var(--accent-ring);}' +
            ".rcd-opt[aria-selected='true']{font-weight:600;color:var(--accent);}";
        document.head.appendChild(st);
    }

    function _buildRegiaoDropdown(select, mapa) {
        if (!select || select.dataset.rcdEnhanced === '1') return;
        select.dataset.rcdEnhanced = '1';
        _injectRcdCss();

        var wrap = document.createElement('div');
        wrap.className = 'rcd';
        var btn = document.createElement('div');
        btn.className = 'rcd-btn ' + (select.className || '');
        btn.setAttribute('tabindex', '0');
        btn.setAttribute('role', 'combobox');
        btn.setAttribute('aria-haspopup', 'listbox');
        btn.setAttribute('aria-expanded', 'false');
        var label = document.createElement('span');
        label.className = 'rcd-label';
        btn.appendChild(label);
        var list = document.createElement('div');
        list.className = 'rcd-list';
        list.setAttribute('role', 'listbox');

        function syncLabel() {
            var opt = select.options[select.selectedIndex];
            label.textContent = opt ? opt.text : '';
            label.classList.toggle('rcd-placeholder', !select.value);
        }

        var rows = [];
        Array.prototype.forEach.call(select.options, function (opt) {
            var row = document.createElement('div');
            row.className = 'rcd-opt';
            row.setAttribute('role', 'option');
            row.textContent = opt.text;
            row.dataset.value = opt.value;
            var cidades = mapa[opt.value];
            if (cidades && cidades.length) {
                row.setAttribute('data-tip', opt.text + '|' + cidades.join(', '));
            }
            row.setAttribute('aria-selected', opt.value === select.value ? 'true' : 'false');
            row.addEventListener('click', function () {
                if (select.value !== opt.value) {
                    select.value = opt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
                syncLabel();
                markSelected();
                close();
            });
            list.appendChild(row);
            rows.push(row);
        });

        function markSelected() {
            rows.forEach(function (r) {
                r.setAttribute('aria-selected', r.dataset.value === select.value ? 'true' : 'false');
            });
        }

        var activeIdx = -1;
        function setActive(i) {
            if (!rows.length) return;
            activeIdx = (i + rows.length) % rows.length;
            rows.forEach(function (r, k) { r.classList.toggle('active', k === activeIdx); });
            rows[activeIdx].scrollIntoView({ block: 'nearest' });
        }
        function open() {
            document.querySelectorAll('.rcd.open').forEach(function (w) { if (w !== wrap) w.classList.remove('open'); });
            wrap.classList.add('open');
            btn.setAttribute('aria-expanded', 'true');
            var sel = -1;
            rows.forEach(function (r, k) { if (r.dataset.value === select.value) sel = k; });
            setActive(sel >= 0 ? sel : 0);
        }
        function close() {
            wrap.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
        }

        btn.addEventListener('click', function () {
            wrap.classList.contains('open') ? close() : open();
        });
        btn.addEventListener('keydown', function (e) {
            var isOpen = wrap.classList.contains('open');
            if (e.key === 'ArrowDown') { e.preventDefault(); isOpen ? setActive(activeIdx + 1) : open(); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); isOpen ? setActive(activeIdx - 1) : open(); }
            else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (isOpen && rows[activeIdx]) rows[activeIdx].click(); else open(); }
            else if (e.key === 'Escape') { close(); }
        });

        select.style.display = 'none';
        select.parentNode.insertBefore(wrap, select.nextSibling);
        wrap.appendChild(btn);
        wrap.appendChild(list);
        select.addEventListener('change', function () { syncLabel(); markSelected(); });
        syncLabel();
    }

    function initRegiaoCustomDropdown(root) {
        var scope = root && root.querySelectorAll ? root : document;
        _fetchRegioesCidades().then(function (mapa) {
            scope.querySelectorAll('select[name="regiao"]').forEach(function (s) {
                _buildRegiaoDropdown(s, mapa);
            });
        });
    }

    // Fechar dropdown ao clicar fora (uma vez só)
    if (!document.__rcdOutside) {
        document.__rcdOutside = true;
        document.addEventListener('click', function (e) {
            document.querySelectorAll('.rcd.open').forEach(function (w) {
                if (!w.contains(e.target)) w.classList.remove('open');
            });
        });
    }

    // Enhancer para selects que aparecem depois (form-modal da agenda, etc.)
    if (!window.__rcdObserver && typeof MutationObserver !== 'undefined') {
        window.__rcdObserver = new MutationObserver(function (muts) {
            for (var i = 0; i < muts.length; i++) {
                var added = muts[i].addedNodes;
                for (var j = 0; j < added.length; j++) {
                    var n = added[j];
                    if (n.nodeType !== 1) continue;
                    if (n.matches && n.matches('select[name="regiao"]')) initRegiaoCustomDropdown(n.parentNode);
                    else if (n.querySelector && n.querySelector('select[name="regiao"]')) initRegiaoCustomDropdown(n);
                }
            }
        });
    }

    // Expose
    window.LiderancasCommon = {
        initPhoneMask: initPhoneMask,
        initCityLoader: initCityLoader,
        initFilterCityLoader: initFilterCityLoader,
        initRegiaoCustomDropdown: initRegiaoCustomDropdown,
    };

    // Auto-init em todos os selects de região (uma vez só)
    if (!window.__rcdInit) {
        window.__rcdInit = true;
        function _rcdStart() {
            initRegiaoCustomDropdown();
            if (window.__rcdObserver) window.__rcdObserver.observe(document.body, { childList: true, subtree: true });
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', _rcdStart);
        } else {
            _rcdStart();
        }
    }
})();

// ===== Menu "⋯" das linhas de listagem =====
// (o arquivo pode ser incluído 2x — base.html e extra_js — então registra uma vez só)
if (!window.__rowMenuBound) {
window.__rowMenuBound = true;
document.addEventListener('click', function (e) {
    const trigger = e.target.closest('[data-row-menu]');
    document.querySelectorAll('.row-menu.open').forEach(function (m) {
        if (!trigger || m !== trigger.nextElementSibling) m.classList.remove('open');
    });
    if (!trigger) return;
    const menu = trigger.nextElementSibling;
    if (!menu || !menu.classList.contains('row-menu')) return;
    if (menu.classList.contains('open')) { menu.classList.remove('open'); return; }
    const r = trigger.getBoundingClientRect();
    menu.classList.add('open');
    const h = menu.offsetHeight || 90;
    const top = (r.bottom + h + 8 > window.innerHeight) ? (r.top - h - 4) : (r.bottom + 4);
    menu.style.top = top + 'px';
    menu.style.left = Math.max(8, r.right - 165) + 'px';
});
}

// ===== Copiar canal (e-mail) com feedback no tooltip =====
window.copyChan = function (btn, text) {
    function feedback() {
        var original = btn.getAttribute('data-tip');
        btn.setAttribute('data-tip', 'Copiado!');
        setTimeout(function () { btn.setAttribute('data-tip', original); }, 1400);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(feedback);
    } else {
        var ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta);
        ta.select(); document.execCommand('copy'); ta.remove();
        feedback();
    }
};

