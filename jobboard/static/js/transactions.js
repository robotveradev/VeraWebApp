$(document).ready(function () {
    let web3 = new Web3(new Web3.providers.HttpProvider('https://rinkeby.infura.io/0SlaMD80FXy5x6oAztb7'));

    function check_txns() {
        for (let i = $('.txn-status[data-success=false]').length - 1; i >= 0; i--) {
            let self = $('.txn-status:eq(' + i + ')');
            console.log('Check: ', self.data('txn'));
            let txn = self.data('txn');
            set_status(self, txn);
        }
        set_pending();
    }

    function set_status(self, txn) {
        let receipt = web3.eth.getTransactionReceipt(txn);
        console.log(receipt);
        if (receipt.status === '0x1') {
            self.attr('data-success', true);
            self.html('<span class="green-text" data-uk-icon="check"></span>')
        } else if (receipt.status === '0x0') {
            self.html('<span class="red-text" data-uk-icon="close"></span>')
        }
    }

    function set_pending() {
        let count = $('.txn-status[data-success=false]').length;
        let $pending = $('#now-pending');
        if (count > 0) {
            $pending.show();
            $pending.find('span').text(count);
        } else {
            $pending.hide();
        }
    }

    let time_block = $("#time_to_block");
    let time_per_block = time_block.data('per-block');
    setInterval(function () {
        let time = Number(time_block.text()) + 1;
        if (time <= time_per_block - 1) {
            time_block.text(time);
        } else {
            time_block.text(0);
            check_txns();
        }
    }, 1000);
    setTimeout(function () {
        check_txns();
    }, 2000)
});
