#  -*- coding: UTF8 -*-

from django.db import models
from datetime import datetime

from sys_base.exceptions import HeliosException
from sys_util.math.eth import d8

from sys_base.hsm.model import SecureModel


class TokenAccount(SecureModel, models.Model):
    """
        Manages a User's token account on the Luna platform
    """

    # NOTE: The values of fields prefixed with [HSM] are used by the HSM to calculate the signature for
    # this record. Whenever one of these fields is updated, the record has to be re-signed by the HSM

    # ==== BEGIN SECURE BLOCK =====================================================================================

    # [HSM] The id of this record. An implicit field in Django, but explicitly called-out here because
    # its under HSM control to prevent an attacker from swapping record ids

    id = models.AutoField(primary_key=True)

    # [HSM] When this record was last updated. No default, since the value has to be explicitly set,
    # because it's signed by the HSM.

    updated = models.DateTimeField(db_index=True)

    # [HSM] The amount of confirmed balance this user has in their account. Up to a million tokens at 18-decimal
    # precision. A DecimalField type specifically configured as below is REQUIRED to prevent math errors when
    # doing even basic math operations. Ethereum cannot be treated as a float.
    #
    # See: http://ethdocs.org/en/latest/ether.html
    # See: https://docs.python.org/2/library/decimal.html#module-decimal

    confirmed_balance = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] The unconfirmed balance this user has in their account. We don't track the number of confirmations
    # here because they could have multiple inbound transactions, each with its own remaining confirmations

    unconfirmed_balance = models.DecimalField(max_digits=20, decimal_places=8, default=d8(0.0), db_index=True)

    # [HSM] The address of the QTUM wallet we've created to receive transfers from this user
    enclave_address = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    # [HSM] The initialization vector used when encrypting this record's data blobs. Every record has a
    # unique iv to prevent an attacker using large numbers of records to reverse the master key.

    data_iv = models.BinaryField(null=True)

    # [HSM] An encrypted JSON blob used by the HSM to store the private key for the enclave_address field
    enclave_data = models.BinaryField(null=True)

    # [HSM] An encrypted JSON blob containing data the HSM uses to decide if a transfer to sovereign
    # address should be approved. By storing the data as an encrypted blob that only the HSM can decrypt
    # and read, it makes it impossible for attackers to trick the HSM into signing a rogue transaction.

    policy_data = models.BinaryField(null=True)

    # [HSM] Current revision of this record
    revision = models.PositiveIntegerField(default=0, db_index=True)

    # [HSM] The HSM signature for this record. Used to detect if the record has been tampered with.
    hsm_sig = models.BinaryField(null=True)

    # ==== END SECURE BLOCK =======================================================================================

    # The last time this account's owner requested that we check their inbound QTUM address balance. Used to
    # prevent someone DOS'ing the API by flooding us with update requests

    last_qtum_sync = models.DateTimeField(default=datetime.now, db_index=True)

    def add_confirmed_balance(self, val):
        """
        Alters the balance by the given val.
        To prevent error in the logic where confirmed balance can be negetive we use this
        method to check for that condition
        :param val: The value to add to the balance
        """
        if self.confirmed_balance + val < 0:
            raise HeliosException(desc='balance cannot be negative', code='invalid_negative_balance')

        self.confirmed_balance += val

    def generate_hsm_hash(self):
        """
            Concatenates all HSM controlled columns in a record into a string, for processing by the HSM
        """

        return ''.join([

            str(self.id),
            str(self.updated),
            str(d8(self.confirmed_balance)),
            str(d8(self.unconfirmed_balance)),
            str(self.enclave_address),
            str(self.data_iv),
            str(self.enclave_data),
            str(self.policy_data),
            str(self.revision)
        ])
