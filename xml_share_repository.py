import xml.etree.ElementTree
import xml_share as xshare


class xml_share_repository:
    """
    Stores the information read from xml for easy access.
    """
    xml_shares = []
    
    def built_up_repository(self, share_file='shares.xml'):
        """
        Fill the repository at start.
        """
        xml_shares_root = xml.etree.ElementTree.parse(share_file).getroot()

        for xml_share_in_file in xml_shares_root.findall('share'):
            xml_share = xshare.xml_share()
            
            for xml_name_temp in xml_share_in_file.findall('name'):
                xml_share.xml_name = str(xml_name_temp.text)
                
            for xml_units_temp in xml_share_in_file.findall('units'):
                xml_share.xml_units = str(xml_units_temp.text)
                
            for xml_buy_price_temp in xml_share_in_file.findall('buyPrice'):
                xml_share.xml_buy_price = str(xml_buy_price_temp.text)
                
            for xml_buy_date_temp in xml_share_in_file.findall('buyDate'):
                xml_share.xml_buy_date = str(xml_buy_date_temp.text)
                
            for xml_trailing_stop_date_temp in xml_share_in_file.findall('trailingStopDate'):
                xml_share.xml_trailing_stop_date = str(xml_trailing_stop_date_temp.text)
                
            for xml_trailing_stop_percentage_temp in xml_share_in_file.findall('trailingStopPercentage'):
                xml_share.xml_trailing_stop_percentage = str(xml_trailing_stop_percentage_temp.text)
                
            for xml_trailing_stop_absolute_temp in xml_share_in_file.findall('trailingStopAbsolute'):
                xml_share.xml_trailing_stop_absolute = str(xml_trailing_stop_absolute_temp.text)
                
            for xml_trailing_stop_init_temp in xml_share_in_file.findall('trailingStopInit'):
                xml_share.xml_trailing_stop_init = str(xml_trailing_stop_init_temp.text)
                
            
            positionToInsert = 0
            
            for entry in self.xml_shares:
                if entry.xml_name < xml_share.xml_name:
                    positionToInsert = positionToInsert + 1
                else:
                    break
                    
            self.xml_shares.insert(positionToInsert, xml_share)