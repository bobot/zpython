import sys
import unittest
from test import support

pwd = support.import_module('pwd')

class PwdTest(unittest.TestCase):

    def test_values(self):
        entries = pwd.getpwall()
        entriesbyname = {}
        entriesbyuid = {}

        for e in entries:
            self.assertEqual(len(e), 7)
            self.assertEqual(e[0], e.pw_name)
            self.assertIsInstance(e.pw_name, str)
            self.assertEqual(e[1], e.pw_passwd)
            self.assertIsInstance(e.pw_passwd, str)
            self.assertEqual(e[2], e.pw_uid)
            self.assertIsInstance(e.pw_uid, int)
            self.assertEqual(e[3], e.pw_gid)
            self.assertIsInstance(e.pw_gid, int)
            self.assertEqual(e[4], e.pw_gecos)
            self.assertIsInstance(e.pw_gecos, str)
            self.assertEqual(e[5], e.pw_dir)
            self.assertIsInstance(e.pw_dir, str)
            self.assertEqual(e[6], e.pw_shell)
            self.assertIsInstance(e.pw_shell, str)

            # The following won't work, because of duplicate entries
            # for one uid
            #    self.assertEqual(pwd.getpwuid(e.pw_uid), e)
            # instead of this collect all entries for one uid
            # and check afterwards
            entriesbyname.setdefault(e.pw_name, []).append(e)
            entriesbyuid.setdefault(e.pw_uid, []).append(e)

        if len(entries) > 1000:  # Huge passwd file (NIS?) -- skip the rest
            return

        # check whether the entry returned by getpwuid()
        # for each uid is among those from getpwall() for this uid
        for e in entries:
            if not e[0] or e[0] == '+':
                continue # skip NIS entries etc.
            self.assertIn(pwd.getpwnam(e.pw_name), entriesbyname[e.pw_name])
            self.assertIn(pwd.getpwuid(e.pw_uid), entriesbyuid[e.pw_uid])

    def test_errors(self):
        self.assertRaises(TypeError, pwd.getpwuid)
        self.assertRaises(TypeError, pwd.getpwnam)
        self.assertRaises(TypeError, pwd.getpwall, 42)

        # try to get some errors
        bynames = {}
        byuids = {}
        for (n, p, u, g, gecos, d, s) in pwd.getpwall():
            bynames[n] = u
            byuids[u] = n

        allnames = list(bynames.keys())
        namei = 0
        fakename = allnames[namei]
        while fakename in bynames:
            chars = list(fakename)
            for i in range(len(chars)):
                if chars[i] == 'z':
                    chars[i] = 'A'
                    break
                elif chars[i] == 'Z':
                    continue
                else:
                    chars[i] = chr(ord(chars[i]) + 1)
                    break
            else:
                namei = namei + 1
                try:
                    fakename = allnames[namei]
                except IndexError:
                    # should never happen... if so, just forget it
                    break
            fakename = ''.join(chars)

        self.assertRaises(KeyError, pwd.getpwnam, fakename)

        # In some cases, byuids isn't a complete list of all users in the
        # system, so if we try to pick a value not in byuids (via a perturbing
        # loop, say), pwd.getpwuid() might still be able to find data for that
        # uid. Using sys.maxint may provoke the same problems, but hopefully
        # it will be a more repeatable failure.
        fakeuid = sys.maxsize
        self.assertNotIn(fakeuid, byuids)
        self.assertRaises(KeyError, pwd.getpwuid, fakeuid)

def test_main():
    support.run_unittest(PwdTest)

if __name__ == "__main__":
    test_main()
