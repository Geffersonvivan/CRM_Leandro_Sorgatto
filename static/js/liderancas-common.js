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

    // Expose
    window.LiderancasCommon = {
        initPhoneMask: initPhoneMask,
        initCityLoader: initCityLoader,
        initFilterCityLoader: initFilterCityLoader,
    };
})();
