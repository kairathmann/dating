#  -*- coding: UTF8 -*-


from plant_hermes.hsm.adapter import HSMadapter


class SecureModel(object):
    """
        Simulates a Hardware Security Module

        ### IN PRODUCTION, ALL FUNCTIONS BELOW WILL RUN INSIDE THE HSM'S CRYPTOGRAPHIC PROCESSOR ###
    """

    def calculate_hsm_sig(self):
        """
            Creates a signature for this record
        """
        return HSMadapter.sign_record(

            plaintext=self.generate_hsm_hash()
        )

    def sig_is_valid(self):
        """
            Verifies this record's signature is valid
        """
        return HSMadapter.verify_record_sig(

            hsm_sig=self.hsm_sig,
            plaintext=self.generate_hsm_hash()
        )
