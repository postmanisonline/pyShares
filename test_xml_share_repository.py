'''
Unit tests for xml_share_repository
'''
import unittest
import xml_share_repository as xsr

TEST_XML_REPOSITORY_COUNT = 3

class Test(unittest.TestCase):


    def test_built_up(self):
        repository = xsr.xml_share_repository()
        repository.xml_shares.clear()
        repository.built_up_repository(share_file='../shares.xml')
        
        self.assertEqual(len(repository.xml_shares), TEST_XML_REPOSITORY_COUNT)
        
        
    def test_all_shares_contained(self):
        repository = xsr.xml_share_repository()
        repository.xml_shares.clear()
        repository.built_up_repository(share_file='../shares.xml')
        
        bmw_contained = False
        psm_contained = False
        rwe_contained = False
        
        for repository_entry in repository.xml_shares:
            if repository.xml_shares[repository_entry].xml_name == 'BMW.DE':
                bmw_contained = True
                
            if repository.xml_shares[repository_entry].xml_name == 'PSM.DE':
                psm_contained = True
                
            if repository.xml_shares[repository_entry].xml_name == 'RWE.DE':
                rwe_contained = True
                
        self.assert_(bmw_contained and psm_contained and rwe_contained, True)
     
     
    def test_psm(self):
        repository = xsr.xml_share_repository()
        repository.xml_shares.clear()
        repository.built_up_repository(share_file='../shares.xml')
        
        for repository_entry in repository.xml_shares:
            if repository.xml_shares[repository_entry].xml_name == 'PSM.DE':  
                self.assertEqual(repository.xml_shares[repository_entry].xml_units, '125')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_price, '39.15')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_date, '2017-01-01')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_date, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_percentage, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_absolute, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_init, 'None')
    
     
    def test_bmw(self):
        repository = xsr.xml_share_repository()
        repository.xml_shares.clear()
        repository.built_up_repository(share_file='../shares.xml')
        
        for repository_entry in repository.xml_shares:
            if repository.xml_shares[repository_entry].xml_name == 'BMW.DE':  
                self.assertEqual(repository.xml_shares[repository_entry].xml_units, '40')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_price, '89.92')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_date, '2017-01-01')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_date, '2017-01-20')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_percentage, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_absolute, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_init, 'None')        


    def test_rwe(self):
        repository = xsr.xml_share_repository()
        repository.xml_shares.clear()
        repository.built_up_repository(share_file='../shares.xml')
        
        for repository_entry in repository.xml_shares:
            if repository.xml_shares[repository_entry].xml_name == 'RWE.DE':  
                self.assertEqual(repository.xml_shares[repository_entry].xml_units, '100')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_price, '12.78')
                self.assertEqual(repository.xml_shares[repository_entry].xml_buy_date, '2017-01-01')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_date, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_percentage, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_absolute, 'None')
                self.assertEqual(repository.xml_shares[repository_entry].xml_trailing_stop_init, 'None')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()