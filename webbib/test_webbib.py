from lxml import etree
import bibmod
import lxml
import py

class Test_Staff:

    def setup_class(self):
        self.s = bibmod.Staff(filename='testdata/test_staff.xml')
        self.s.load_staff()

        # add one Staff-member:
        a = "<author><lastname>ln4</lastname><firstname>fn4</firstname></author>"
        axml = etree.fromstring(a)
        a = self.s.add_author_to_dict(axml, current=False)
        self.s.authors[(a.get('lastname'), a.get('firstname'))] = a


    def test_load_staff_len(self):
        assert len(self.s.authors) == 4

    def test_load_staff_content(self):
        assert self.s.authors[('Lastname2','Firstname2')] == \
            {'current': True, 'firstname': 'Firstname2', 'lastname': 'Lastname2'}

    def test_load_staff_current(self):
        assert self.s.authors[('Lastname3','Firstname3')].get('current') == False

    def test_load_staff_keys(self):
        assert len(self.s.authors.keys()) == 4

    def test_add_author_to_dict(self):
        assert self.s.authors[('ln4', 'fn4')] == \
            {'current': False, 'firstname': 'fn4', 'lastname': 'ln4'}

    def test_author_is_staff_1(self):
        assert self.s.author_is_staff('Lastname3','Firstname3') == \
            {'current': False, 'firstname': 'Firstname3', 'lastname': 'Lastname3'}

    def test_author_is_staff_2(self):
        assert self.s.author_is_staff('Lastname3','F.') == \
            {'current': False, 'firstname': 'Firstname3', 'lastname': 'Lastname3'}

    def test_author_is_staff_3(self):
        assert self.s.author_is_staff('ln4','fn4') == \
            {'current': False, 'firstname': 'fn4', 'lastname': 'ln4'}
    
    def test_get_staff_list_1(self):
        assert len(self.s.get_staff_list()) == 2

    def test_get_staff_list_2(self):
        assert len(self.s.get_staff_list(False)) == 2

    def test_get_staff_list_3(self):
        assert self.s.get_staff_list()[0] == \
            {'current': True, 'firstname': 'Firstname1', 'lastname': 'Lastname1'}
