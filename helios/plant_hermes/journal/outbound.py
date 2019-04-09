#  -*- coding: UTF8 -*-

from datetime import datetime

from django.db import models

from sys_base.hsm.model import SecureModel

from sys_util.math.eth import d8


class JournalOut(SecureModel, models.Model):
    """
        Journals transfers OUT to the platform to user wallets
    """

    # NOTE: The values of fields prefixed with [HSM] are used by the HSM to calculate the signature for
    # this record. Whenever one of these fields is updated, the record has to be re-signed by the HSM

    # ==== BEGIN SECURE BLOCK =====================================================================================

    # [HSM] The id of this record. An implicit field in Django, but explicitly called-out here because
    # its under HSM control to prevent an attacker from swapping record ids

    id = models.AutoField(primary_key=True)

    # [HSM] When this record was created. No default, since the value has to be explicitly set,
    # because it's signed by the HSM.

    created = models.DateTimeField(default=datetime.now, db_index=True)

    # [HSM] User that this payment was sent to. Set to PROTECT against accidental CASCADE_DELETE.
    user = models.ForeignKey('silo_user.User', related_name='trans_out', on_delete=models.PROTECT)

    # [HSM] The amount of tokens that were sent
    #
    # A DecimalField type specifically configured as below is REQUIRED to prevent math errors when
    # doing even basic math operations. Ethereum cannot be treated as a float.
    #
    # See: http://ethdocs.org/en/latest/ether.html
    # See: https://docs.python.org/2/library/decimal.html#module-decimal

    amount = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] Fee that Luna charged to run this transaction
    luna_fee = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] Total proceeds sent to destination address
    total = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] The address of the QTUM wallet we sent this payment to
    dest_address = models.CharField(max_length=64, db_index=True)

    # [HSM] Transaction id
    txid = models.CharField(max_length=128, db_index=True)

    # [HSM] The amount of gas it cost us to send these tokens
    send_gas = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] The HSM signature for this record. Used to detect if the record has been tampered with.
    hsm_sig = models.BinaryField(null=True)

    # ==== END SECURE BLOCK =======================================================================================

    def generate_hsm_hash(self):
        """
            Concatenates all HSM controlled columns in a record into a string, for processing by the HSM
        """

        return ''.join([

            str(self.id),
            str(self.created),
            str(self.user_id),
            str(d8(self.amount)),
            str(d8(self.luna_fee)),
            str(d8(self.total)),
            str(self.dest_address),
            str(self.txid),
            str(d8(self.send_gas))
        ])
