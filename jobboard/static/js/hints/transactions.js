$(document).ready(function () {
    if (typeof hint_set !== "undefined") {
        let transactions = {
            title: 'transactions',
            steps: [
                {
                    'next table': 'Here you may see<span class="hint-green">Trnsaction info</span>. <br/>' +
                    'TX HASH <span class="hint-green">its a unique key of transaction, you may check transaction status by this key</span> .<br>' +
                    'Also you may see your vacancies subscribe in <span class="hint-green"> action column</span>',
                    showSkip: false,
                    showNext: true
                }
            ],
        };
        hint_set.push(transactions);
    }
});