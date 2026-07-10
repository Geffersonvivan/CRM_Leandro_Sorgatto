/**
 * Form Modal — abre formulários de cadastro/edição num modal via AJAX.
 * Uso: <a href="/url/do/form/" onclick="return openFormModal(this.href, 'Título')">
 * O servidor devolve o parcial _form_fields.html para requisições XHR e
 * JSON {ok: true} quando o salvamento dá certo.
 */
(function () {
    'use strict';

    let overlay = null;
    let currentUrl = '';

    function build() {
        if (overlay) return;
        overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'formModal';
        overlay.innerHTML =
            '<div class="form-modal-box">' +
            '  <div class="form-modal-header">' +
            '    <span class="modal-title" id="formModalTitle"></span>' +
            '    <button class="modal-close" type="button" data-close>&times;</button>' +
            '  </div>' +
            '  <div class="form-modal-body" id="formModalBody"></div>' +
            '  <div class="form-modal-footer">' +
            '    <button type="button" class="btn btn-outline" data-close>Cancelar</button>' +
            '    <button type="button" class="btn btn-primary" id="formModalSubmit">Salvar</button>' +
            '  </div>' +
            '</div>';
        document.body.appendChild(overlay);
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay || e.target.hasAttribute('data-close')) closeFormModal();
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeFormModal();
        });
        document.getElementById('formModalSubmit').addEventListener('click', function () {
            const f = document.getElementById('formModalForm');
            if (f) f.requestSubmit ? f.requestSubmit() : f.submit();
        });
    }

    function initWidgets() {
        if (window.LiderancasCommon) {
            LiderancasCommon.initPhoneMask('#formModal #id_telefone');
            LiderancasCommon.initCityLoader('#formModal #id_regiao', '#formModal #id_cidade');
            // Isadora: busca na cidade + preenchimento derivado de Meso/Micro/Assoc.
            LiderancasCommon.initCidadeSearch('#formModal');
            LiderancasCommon.initCidadeDerivados('#formModal');
        }
        const form = document.getElementById('formModalForm');
        if (form) form.addEventListener('submit', onSubmit);
    }

    function onSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const btn = document.getElementById('formModalSubmit');
        btn.disabled = true;
        btn.textContent = 'Salvando...';
        fetch(currentUrl, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(async function (r) {
                const ct = r.headers.get('content-type') || '';
                if (ct.indexOf('application/json') !== -1) {
                    const d = await r.json();
                    if (d.ok) { window.location.reload(); return; }
                    alert(d.error || 'Não foi possível salvar.');
                    closeFormModal();
                } else {
                    document.getElementById('formModalBody').innerHTML = await r.text();
                    initWidgets();
                }
            })
            .catch(function () { alert('Erro de conexão. Tente novamente.'); })
            .finally(function () {
                btn.disabled = false;
                btn.textContent = 'Salvar';
            });
    }

    window.openFormModal = function (url, title) {
        build();
        currentUrl = url;
        document.getElementById('formModalTitle').textContent = title || '';
        document.getElementById('formModalBody').innerHTML =
            '<div class="form-modal-loading"><span class="spinner"></span> Carregando...</div>';
        overlay.classList.add('active');
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' }, cache: 'no-store' })
            .then(function (r) {
                if (!r.ok) throw new Error('http');
                return r.text();
            })
            .then(function (html) {
                document.getElementById('formModalBody').innerHTML = html;
                initWidgets();
                const first = document.querySelector('#formModalBody input:not([type=hidden]), #formModalBody select, #formModalBody textarea');
                if (first) first.focus();
            })
            .catch(function () { window.location.href = url; });
        return false;
    };

    window.closeFormModal = function () {
        if (overlay) overlay.classList.remove('active');
    };
})();
