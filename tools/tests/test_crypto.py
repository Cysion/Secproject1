from django.test import TestCase

from tools import crypto


class TestCrypto(TestCase):

    def setUp(self):
        """ Sets up testing environment """

        self.rsa_keypair = (
            b'-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQCMFyqLfkhUI8NUFVbUFl5E9LQMlyrnGR8pWbm+FWFN45psFEvJ\namKU1ADx5UKi4pZo7MTX6gHaiQ1RTDQ2xwKnWmvdJk6ih47Px4f+bXAzJr3k6XXt\nbAx2vm14Gt5FpbdGuJz+LuQRHetsQvXmjM4yX7TmRbRjSD/Qz4HpNaEwxwIDAQAB\nAoGAASAchONeVGK3KoFDYc/OMRKgMauzOgkPIYdpgRft4LDP6Edfdn5GzXhIi6jy\nWJmmaLBiQnPMUQOh2kHY94mwwUFjMOUQ4X7Uuw3AGeCqz4HmbCkWEhKRyBNVUHrU\noaQrfL2agna3CJ1cjhw7P37UnJOZ9kOdCgRkBZNnwr0xT/0CQQC6/5C0EPITpWIe\nDC0RkIga/sNbXGbdJ2SxtjsD5+PPz9lp0rej+Pj5wXOati/vfrvpzhP9qYvAh0EO\ngVrwSYCtAkEAv8iLh/y/bEPsVYikAlDf8Uf5rhQZkxlFDEh4GJwzQQ4gMjlYqsSF\nmAwU9luPrYwLJK66LSb60OEtkikV86GBwwJBAKV5xgkx/aXY8ex5BeDHL0oEK8fL\nCtOlKnwAMFUSfQvGeDQm3Y7ioSASSkSb9+tNEOijDhmoURz8E1vMqDZ+NLkCQAdP\nW5IpXhqAVEfGV4oHDyIhPjEWbwseUXVwZbN6cLGwGiYP7YNEzlrHSx1AzC8vQVV6\nm3oRHEpN6vDBRCbvJwUCQBtrkBHFJizjMuQz5SU3U8V1+dItKpuVCDogFV5kxcdb\nN0h4pvYE48t07k6/KCQRXjNTR2vCPPVN7crxRqN0jWk=\n-----END RSA PRIVATE KEY-----',
            b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCMFyqLfkhUI8NUFVbUFl5E9LQM\nlyrnGR8pWbm+FWFN45psFEvJamKU1ADx5UKi4pZo7MTX6gHaiQ1RTDQ2xwKnWmvd\nJk6ih47Px4f+bXAzJr3k6XXtbAx2vm14Gt5FpbdGuJz+LuQRHetsQvXmjM4yX7Tm\nRbRjSD/Qz4HpNaEwxwIDAQAB\n-----END PUBLIC KEY-----'
        )

    def test_secret_scrambler(self):
        """ Verifies secret_scrambler calculates correct scrypt """

        passw_first = "passw_first"
        salt_first = 123
        blen_first = 128
        result_first = b"^\x7f\xe6\xe3\xf4fSc\xcb\xe8\x97\x86I\xe5 \xe2\x86\xb4R\xca\xc2im^\x9fq\xd5\xe0\x14\xeal\x00\x14`\x8a\xc1\xc9_\xf5\xd4\xbdV#\xdb\x9b\xb4`O\xdc\xcf\x8c\xb3\xb97%'\xd0\xa0>\xd0@\x89U\xfd`\xb79\xe2\xb2\xf1_\x8d8\x9b\x97\x08G5\xa8\xc1u\xa5\xf2*\x8b\xdf2b\xb7\xb3\x9b\xf8\x01\x83\xf9\x17\x11\xd8\xc1\x17\xcf\xdcBF\xcf\xee\xc8\t\t\xcapih_\xd2\xdd\xd8\xd1\xf9\x17tm?\xd7\xcd\x08rC"

        passw_second = "passw_second"
        salt_second = 321
        blen_second = 256
        result_second = b'\xdf\x12q\xba\x14}\x9e\x16\xe7(\xb5\xe2\xb0\xbe\xa8\x7fn@v\x07\x14x\xec\x91N\x8b\xed\xcd\xde\xa8c_\xa0% \xfc#\n\xa2\x8co\xe5\xef\'D\x91\xe2\xaa\x96o!\x01t\xc0\xda\x87\x8e\xaf\x90\xfeh\xda\rii\x19\xfc\xda\x10\rg!\x1e\x9b\xe4\xb0*\x1eP\xbd\x07 \x97\xa8\x90\x1fD\xbb\x91\xfai;\x1f\xf9\x81"\xf4\x0e\x13R\xb30\xa9A\'\x00\x1d\xc6\x8d\xc1\x80\xd9\xbb)\x9d`\xdb\xd2\xe7\xb8"\xfeK\xb1\xd6\xee\x93\xf2\xfd\xf7\x97\xc0f\xb5W\xe6\xc8\xa9\xbc\xaed\x94\xbd\x81\x97,"\x9c\xe8&\x89a\x96\xa4\xc1u\x7fA\x01\x99\xd1\x18h3:\xab\x84\x91f\xb1\x1d-\x14\xc1\x8aqM\xd2\xbe|\x06\xe3yT\xe488N\xb9x\t8P\xabfoy\xd6\x08\'\x00Q\xb2\xb4\x89\x1d0\xea\xf0\xb4\xbd\x8a%@x\x8f+\x8cf\x86\x88&\xef>\xeaK.J\rD\xab\xef\x9e*\xf2\xdf=\xeaG\x9ey\xbe\\\x18E\xf4S\xaa\xe45\xb3\xe8I2\x9e\x17'

        self.assertEqual(str(secret_scrambler(passw_first, salt_first, blen_first)), result_first)
        self.assertEqual(str(secret_scrambler(passw_second, salt_second, blen_second)), result_second)


    def test_qdigest(self):
        """ Verifies qdigest calculates correct hash """

        test_input1 = "This is the first test string."
        test_input2 = "This is the second test string."

        test_output1 = "4be24e5b5cdb7e525d1bcfc5e48aa28ecc8598b2"
        test_output2 = "91278416f3f4624b73ca562ff44beffd84f719ea"

        self.assertEqual(crypto.qdigest(test_input1.encode("utf-8")), test_output1)
        self.assertEqual(crypto.qdigest(test_input2.encode("utf-8")), test_output2)


    def test_gen_rsa(self):
        """ Verifies gen_rsa calculates key of correct length """

        bits_first = 2048
        bits_second = 1024

        scram = secret_scrambler("password", 123)

        key_first = crypto.gen_rsa(scram, bits_first)
        key_second = crypto.gen_rsa(scram, bits_second)

        self.assertEqual(len(key_first.export_key()), 1674)
        self.assertEqual(len(key_first.publickey().export_key()), 450)
        self.assertEqual(len(key_second.export_key()), 886)
        self.assertEqual(len(key_second.publickey().export_key()), 271)


    def test_rsa_encrypt(self):
        """ Verifies rsa_encrypt encrypts data properly """

        data = b"When you're a kid, you don't realize you're also watching your mom and dad grow up."
        result = b'\x0f\x8d\xcd\x9by\xb6\xb8\xb7!\xe6\xff1\xc3\x0b\xfa\xba\xf1\xd0\xde\xcd\xac\xb9\xd1{\xef6\x07\xef\xa0\xa9\x18\xdc\xbf\x1fA\x1c5\xce\xc5LB(\xbf\x1f\x8ar\x0e\x88U\x9c\x9b\x1cg]\x8f\xbd\xd1\xae\xe4\x95.\r\xd0\xd2@\n\x11_<\xc4\x16\xfb8\x0ep\x06\x1cr:\nU\x0c\xc8L\xa0\x1d/\xa5\x11-1J\xc3\xdaQ \xcaam=\x05\x8a\xda\x80\x91\xf2\n\xcc\x83\xa7M\xbe6\x92:\x8d\n\t\xa6\xbf\xab/\xa18?\x93#\xa2'

        self.assertEqual(crypto.rsa_encrypt(self.rsa_keypair[1], data), result)


    def test_rsa_decrypt(self):
        """ Verifies rsa_decrypt decrypts data properly """

        data = b'\x0f\x8d\xcd\x9by\xb6\xb8\xb7!\xe6\xff1\xc3\x0b\xfa\xba\xf1\xd0\xde\xcd\xac\xb9\xd1{\xef6\x07\xef\xa0\xa9\x18\xdc\xbf\x1fA\x1c5\xce\xc5LB(\xbf\x1f\x8ar\x0e\x88U\x9c\x9b\x1cg]\x8f\xbd\xd1\xae\xe4\x95.\r\xd0\xd2@\n\x11_<\xc4\x16\xfb8\x0ep\x06\x1cr:\nU\x0c\xc8L\xa0\x1d/\xa5\x11-1J\xc3\xdaQ \xcaam=\x05\x8a\xda\x80\x91\xf2\n\xcc\x83\xa7M\xbe6\x92:\x8d\n\t\xa6\xbf\xab/\xa18?\x93#\xa2'
        result = b"When you're a kid, you don't realize you're also watching your mom and dad grow up."

        self.assertEqual(crypto.rsa_decrypt(self.rsa_keypair[0], data), result)


    def test_get_anon_id(self):
        """ Verifies get_anon_id generates ID correctly and consistently """

        uid_first = 123
        birthday_first = "2020-01-01"
        blen_first = 256
        result_first = b"\xa5\x93\x01BU\x7fi\xb4\x05\xbe\xee\xa3\xb75\xe1\x1c*\xd9\xa8\xf6\xd4ek\xbaC.QF\x84\xde\x9d&\xf4(\x9bE\xf2\xf3<U*{&]\xd5\xea\xd4<\xee\xad\xe1w.\xf8\x01\x17\x95y\xb0\x9e\x9cG\x19\x81m\xc2\x11?8S0\xa9\xdb\x08\x83:D\xfe\x8f\xbd\x13v\x9e'\xcb\xaf\xb6\xca|>Dg\x16\x0e\x8abM\xa2\xfb\x18\xcf\xa4\xfd\xe3&F\x00\r\xf4\xbd\x80\xe0\xcf\x9a=;y\x8aO\xe2\x0e6\x05H\t\xe4\xf6\xdd0L\xb9\xd0P`F\xe0\xce\xe6\xaf=&l\xf0\xd7=\xbc\xdd}#_\xab\xc6\xbb\x10\xbf?\xb3\xe6:\x9c\xad\r\xe1\xac\xdfa\xe19\xf1\xa95\xca\x959\x93\xae3H\x0c\x01\x02<5.^\x81\xc4\x0eK\xfb\xb3(\x06K\xabWg\x0f+P\x83N\x8c\x8f\xdb\xf2\x1f\xe3\xad0\xcc\xfbS\xf0R!\x19\xbc\x89;\x97\xb7\xef\xd6\x99\n\x92\xaa\x88B\xe8\x1d\t$W\x81f\x95m\xf6l\x13\x8f\xbd\xeb\xf9|\x9e\xd3\xa9j\\a&5F"

        uid_second = 321
        birthday_second = "2021-01-02"
        blen_second = 128
        result_second = b'\xff\x0b;\xf8\xf40\xb3}\x9a\x85\x01\xcf\xd5\x8e\x17\x0f\xa8\x8f\x83o\x8d\xc9\xb8\xa8\xffFJW\x82\xd6\xa0|\x8c\x8e*ou\x99S\x99\xe8\xfe\xa14d\x97\xfc\x80T\x1f\xfcjVIJ#\xabfM\xb6\xa7\x84\\\x19\xdf\x8e\x87\xb8\x8b\x8ef(\xb3Wv%\xfc\x1b\xf2C\x94\xa0";k$\r\x15a\xa4c\xfec\x88}L\xd4\xf0[|\xceTc~\xcd\x8b\x83U\x887\xdf?\x1az\xa0\xc6\xe7x\xa6I\xd6o\xbb2\xadg\xd2{'

        self.assertEqual(get_anon_id(uid_first, birthday_first, blen_first), result_first)
        self.assertEqual(get_anon_id(uid_second, birthday_second, blen_second), result_second)


