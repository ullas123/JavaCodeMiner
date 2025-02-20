import re
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DemographicMatch:
    category: str
    field_name: str
    file_path: str
    line_number: int
    matched_text: str

class DemographicPatternAnalyzer:
    def __init__(self):
        self.demographic_patterns = {  
            'Demographic1': r'\b(Additional Info|Address City|Address Country|Address Postal Code|Address State|Address Street 1|Address Street 2|First Name)\b',
            'Demographic2': r'\b(Full Name|Gender|Generation|ID Number|Last Name|Middle Name|Phone Number|Title|ID Date Expires|ID Date Issued|ID Issued By|ID Label)\b',
            'Demographic3': r'\b(Account Date|Account Group ID|Account Other Data|Account Provider ID|Account Type|Account Amount)\b',
            'id': r'\b(customerId|cm_15)\b',
            'name': r'\b(first_name|last_name|full_name|name|amount)\b',
            'address': r'\b(address|street|city|state|zip|postal_code)\b',
            'contact': r'\b(phone|email|contact)\b',
            'identity': r'\b(ssn|social_security|tax_id|passport)\b',
            'demographics': r'\b(age|gender|dob|date_of_birth|nationality|ethnicity)\b',
            'cmdl': r'\b(cmdl|birth_dt|gend_cd|est_incom_rnge_tx|cust_xref_id|first_nm|mid_nm|last_nm|ad_eff_dt|state_tx|ctry_cd)\b',
            'crps': r'\b(crps|cm13|acct_nbr_noncard|cust_xref_id|acct_mkt_id_cd|addr01_ctry_cd|addr01_pstl_cd_tx|acct_smry_role_typ|acct_pers_gend_cd|acct_birth_dt|AlternateAcctId|AlternateAcctContextCd)\b',
            'DCPs': r'\b(emailAddress|bouncing|emailPurpose)\b',
            'DCPe': r'\b(cm13|ad_prps_cd|capt_ts|email_ad|bounce_in|bounce_dt|purpose_code)\b',
            'DCPm': r'\b(sms_Device|ISD _cd|bounce_in|bounce_dt)\b',
            'Gcud': r'\b(cd_pr1_addr_line_1|cm15|cd_pr1_addr_1|cd_pr1_city_state_1|cd_pr1_state|cd_org)\b',
            'Gad': r'\b(acc_income_amt|acc_stat_cd|acc_block_cd_1|acc_dt_block_cd_1|acc_block_cd_2|acc_dt_block_cd_2|cm13|acc_dt_opened)\b',
            'Gcd': r'\b(crd_gfs_first_name|cm13|card_gfs_crnt_card_in|cm15|crd_logo|cm11|crd_date_opened|crd_gfs_surname_1|crd_org|card_gfs_act_card_in|crd_gender|crd_stat_cd|crd_dt_card_blocked|crd_curr_pct_id|crd_dob|crd_region|crd_country_code|crd_amed_date_expire|crd_memb_since_dt|crd_card_block_cd|crd_city)\b',
            'MEMs': r'\b(first_name|last_name|embossed_name|postal_code|line_of_business_type|account_status|purpose|city|country_code|state|street_address_line1|street_address_line2|street_address_line3|is_basic|supplementary_account_count)\b',
            'Tridemo': r'\b(gainbrplstvalidd|cm13|gaidatelaststatchgd|gaicodeplyrlangd|cshbasicsuppin|gaidateeffd|gaidateplsteffd|gaidatebirthd|gaicodeiaprodidd|gaiaddrpostcoded|gaiaddrctrycoded|gaicodeacctstatd|gaicodeplststatd|gaiamttotincmscnd|gaicodestmtaddrd|gaiaddrtyped|gaiaddrline1d|gaiaddrtyped1|gaiaddrline1d1|gaiaddrtyped2|gaiaddrline1d2|gaiaddrtyped3|gaiaddrline1d3|gaiaddrtyped4|gaiaddrline1d4|gaifirstnamed|gailastnamed|gaiaddrline2d|gaiaddrline2d1|gaiaddrline2d2|gaiaddrline2d3|gaiaddrline2d4|gaiaddrcityd|gaiaddrcityd1|gaiaddrcityd2|gaiaddrcityd3|gaiaddrcityd4|gaiaddrstd|gaiaddrstd1|gaiaddrstd2|gaiaddrstd3|gaiaddrstd4|gaidatefirstused|gaidateplstexprd|gaidatefirstyear|gaicmcodegenderd)\b'
        }
        self.matches = []

    def analyze_code(self, file_path: str, content: str) -> None:
        """
        Analyze the given code content for demographic patterns.
        This is the main entry point for code analysis.

        Args:
            file_path: Path to the file being analyzed
            content: The source code content to analyze
        """
        self.analyze_file(file_path, content)

    def analyze_file(self, file_path: str, content: str) -> None:
        lines = content.split('\n')
        for line_number, line in enumerate(lines, 1):
            for category, pattern in self.demographic_patterns.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    self.matches.append(DemographicMatch(
                        category=category,
                        field_name=match.group(),
                        file_path=file_path,
                        line_number=line_number,
                        matched_text=match.group()
                    ))

    def get_pattern_summary(self) -> Dict[str, List[DemographicMatch]]:
        summary = {}
        for match in self.matches:
            if match.category not in summary:
                summary[match.category] = []
            summary[match.category].append(match)
        return summary

    def get_statistics(self) -> Dict[str, int]:
        return {category: len([m for m in self.matches if m.category == category])
               for category in self.demographic_patterns.keys()}

    def get_patterns(self) -> Dict[str, List[DemographicMatch]]:
        """
        Get all detected patterns grouped by type.
        This method is called by the main application to display results.

        Returns:
            Dict mapping pattern types to lists of matches
        """
        return self.get_pattern_summary()