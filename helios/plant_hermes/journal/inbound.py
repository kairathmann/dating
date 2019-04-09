#  -*- coding: UTF8 -*-

from django.db import models
from datetime import datetime

from sys_base.hsm.model import SecureModel

from sys_util.math.eth import d8


class JournalIn(SecureModel, models.Model):
    """
        Journals transfers IN to the platform from users
    """

    # NOTE: The values of fields prefixed with [HSM] are used by the HSM to calculate the signature for
    # this record. Whenever one of these fields is updated, the record has to be re-signed by the HSM

    # ==== BEGIN SECURE BLOCK =====================================================================================

    # [HSM] The id of this record. An implicit field in Django, but explicitly called-out here because
    # its under HSM control to prevent an attacker from swapping record ids

    id = models.AutoField(primary_key=True)

    # [HSM] When this record was created.
    created = models.DateTimeField(default=datetime.now, db_index=True)

    # [HSM] User that this payment was received from. Set to PROTECT against accidental CASCADE_DELETE.
    user = models.ForeignKey('silo_user.User', related_name='trans_in', on_delete=models.PROTECT)

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

    # [HSM] Total proceeds credited to user
    total = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] The id of OUR transaction to move these tokens to the cold wallet
    txid = models.CharField(max_length=128, db_index=True)

    # [HSM] Amount of gas it cost to transfer these tokens from the USER wallet to the COLD wallet
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
            str(self.txid),
            str(d8(self.send_gas))
        ])
