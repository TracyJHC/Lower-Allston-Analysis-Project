***Project Information*** 
| **Field**                | **Details**                                                                                                                                                                                                                      |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Project Name**         | Data-Driven Identification and Outreach for Affordable Senior Housing in Allston-Brighton                                                                                                |
| **GitHub Repository**    | [GitHub Link](https://github.com/BU-Spark/ds-abcdc-allston/tree/fa25-team-a-dev/fa25-team-a)                                                                                             |
| **Google Drive Folder**  | [Google Drive Link](https://drive.google.com/drive/folders/1ipyNH8VLn5hWSxT3HagitOkVwNoYKo2V?usp=drive_link)                                                                             |
| **Client Organization**  | Allston Brighton Community Development Corporation (ABCDC)                                                                                                                               |
| **Client Contact**       | Daniel                                                                                                                                                                                   |
| **Course**               | DS701 - Tools for Data Science                                                                                                                                                           |
| **Team Members (Team A)**| Achuthan Rathinam, Jinghan (Tracy) Cui, Yang Lu, Xin Wei, Harsha Joshi, Xiaolin (Eric) Tian                                                                                             |

---

### Project Description and Goals


Below, each team member provides their perspective on the project’s purpose and objectives:

- **Achuthan Rathinam:**  
  Many seniors in Allston-Brighton are struggling with housing issues such as high costs, accessibility problems, and social isolation. ABCDC is creating new affordable housing for seniors, but they need better information to reach the right people. This project will gather and organize data to show where seniors live, what their housing situations are, and what needs they may have. The goal is to help ABCDC plan more fairly and make outreach more effective.

- **Jinghan (Tracy) Cui:**  
  The problem we’re trying to solve is how to support older adults in Allston-Brighton who want to age in place but face growing challenges due to rising housing costs, limited accessibility, and the risk of social isolation. This project is an opportunity to use data to better understand where these residents live and what their housing needs are, so that outreach and new housing developments can be planned more equitably and effectively.

- **Yang Lu:**  
  We are interacting with the data and proposing recommendations on improving housing access for the elderly in the Harvard Allston neighbourhood. By analyzing the Voter List (over 40,000 entries), we use it as a proxy for demographic data to identify elderly residents in need of housing assistance, such as vouchers or relocation support, and to assess their access to neighborhood resources.

- **Xin Wei:**  
  Given the voter list of the Allston-Brighton region, we aim to identify and profile patterns among the elderly who are most likely to be eligible for and benefit from newly planned affordable housing. The goal is to build a data-driven foundation for ABCDC to wisely plan housing development and resource allocation.

- **Harsha Joshi:**  
  ABCDC wants to identify the elderly population in Allston-Brighton for their affordable senior housing plan. There is limited understanding about where they live, their housing situations, and the barriers they face. This lack of information makes it hard to target those most in need. The goal is to build a foundation to help ABCDC plan wisely.

- **Xiaolin (Eric) Tian:**  
  Using the data to find patterns of housing accessibility for the elderly population around the Allston area, then predict how to relocate those with financial struggles and facility accessibility difficulties.


***Dataset Information***

**Datasets Used in This Project**

**Dataset Location**

- All datasets used in this project are organized and stored in the following directory within the project repository:

  [fa25-team-a/data](../fa25-team-a/data)

- *Note: This directory will be updated as new datasets are acquired or added throughout the project lifecycle. Please refer to this path for the most current data files.*

* Data dictionaries for the datasets used in this project can be found here: [Data Dictionary](../fa25-team-a/data/data_dictionary.md)

* What keywords or tags would you attach to the data set?  
  * Domain(s) of Application: Other (Demographic Analysis, Geographic Analysis, Housing Policy Analysis)
  * Sustainability, Health, Civic Tech, Voting, Housing, Policing, Budget, Education, Transportation, etc. 
    * **Primary:** Housing, Civic Tech, Health
    * **Secondary:** Voting, Demographics, Geographic Analysis, Social Services 

*The following questions pertain to the datasets you used in your project.*   
*Motivation* 

* For what purpose was the dataset created? Was there a specific task in mind? Was there a specific gap that needed to be filled? Please provide a description.

The voter registration dataset was created by the City of Boston for electoral administration and voter management purposes. The specific gap that our project addresses is the lack of comprehensive demographic and geographic analysis of elderly residents (aged 62+) in the Allston-Brighton neighborhood for affordable senior housing planning. While the dataset was originally created for voting purposes, we repurpose it as a demographic proxy to identify elderly residents who may be eligible for and benefit from affordable senior housing developments. This addresses ABCDC's need for data-driven outreach and housing development planning. 

*Composition*

* What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)? Are there multiple types of instances (e.g., movies, users, and ratings; people and interactions between them; nodes and edges)? What is the format of the instances (e.g., image data, text data, tabular data, audio data, video data, time series, graph data, geospatial data, multimodal (please specify), etc.)? Please provide a description.   

The dataset consists of individual voter registration records representing registered voters in Wards 21 and 22 of Boston (Allston-Brighton neighborhood). Each instance represents one registered voter and contains tabular data with demographic and geographic information. The data format is structured tabular data with mixed data types (strings, integers, dates).

* How many instances are there in total (of each type, if appropriate)?  

- **Total registered voters:** 43,759 instances
- **Elderly residents (62+ years):** 7,384 instances (16.9% of total population)
- **Ward 21:** 4,192 elderly residents
- **Ward 22:** 3,192 elderly residents

* Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set? If the dataset is a sample, then what is the larger set? Is the sample representative of the larger set? If so, please describe how this representativeness was validated/verified. If it is not representative of the larger set, please describe why not (e.g., to cover a more diverse range of instances, because instances were withheld or unavailable).  

The dataset contains all registered voters in Wards 21 and 22 as of the data collection date. It is not a sample but represents the complete voter registration database for these specific wards. However, it should be noted that this dataset only includes registered voters, not the entire population of the area. Non-citizens, unregistered residents, and those who have not registered to vote are not included.

* What data does each instance consist of? "Raw" data (e.g., unprocessed text or images) or features? In either case, please provide a description.   

Each instance consists of processed/cleaned voter registration data with the following fields:
- **Res ID:** Unique resident identifier (string)
- **Street .:** Street number (integer)
- **Sffx:** Street suffix (string, often empty)
- **Street Name:** Full street name (string)
- **Apt .:** Apartment number (string, if applicable)
- **Zip:** ZIP code (integer)
- **Ward:** Ward number (integer: 21 or 22)
- **Precinct:** Precinct number (integer)
- **DOB:** Date of birth (date)
- **Occupation:** Occupation or "UNKNOWN" (string)

* Is there any information missing from individual instances? If so, please provide a description, explaining why this information is missing (e.g., because it was unavailable). This does not include intentionally removed information, but might include redacted text.   

Minimal missing data exists in optional fields such as street suffix (Sffx) and apartment number (Apt .), which are often empty for single-family homes. Occupation data has a high proportion of "UNKNOWN" values, likely because this information is optional during voter registration and many voters choose not to provide it.

* Are there recommended data splits (e.g., training, development/validation, testing)? If so, please provide a description of these splits, explaining the rationale behind them  

No specific data splits are recommended for this dataset as it is used for descriptive analysis and demographic profiling rather than predictive modeling. The analysis focuses on geographic and demographic segmentation (by ward, precinct, and street) for outreach planning purposes.

* Are there any errors, sources of noise, or redundancies in the dataset? If so, please provide a description.   

The dataset appears to be well-maintained with minimal errors. Some potential sources of noise include:
- Inconsistent occupation reporting (many "UNKNOWN" values)
- Potential address formatting variations
- Age calculations based on DOB may have minor discrepancies due to leap years

* Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)? If it links to or relies on external resources,   
  * Are there guarantees that they will exist, and remain constant, over time;  
  * Are there official archival versions of the complete dataset (i.e., including the external resources as they existed at the time the dataset was created)?  
  * Are there any restrictions (e.g., licenses, fees) associated with any of the external resources that might apply to a dataset consumer? Please provide descriptions of all external resources and any restrictions associated with them, as well as links or other access points as appropriate.   

The dataset is self-contained and does not rely on external resources. It was provided directly by the client (ABCDC) and represents a snapshot of voter registration data at a specific point in time.

* Does the dataset contain data that might be considered confidential (e.g., data that is protected by legal privilege or by doctor-patient confidentiality, data that includes the content of individuals' non-public communications)? If so, please provide a description.   

The dataset contains voter registration information which is generally considered public information in Massachusetts, but it does include personal identifiers (Res ID) and addresses that could be considered sensitive. The data should be handled according to privacy best practices and used only for the intended housing outreach purposes.

* Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety? If so, please describe why.   

No, the dataset contains standard demographic and geographic information that is not offensive or threatening in nature.

* Is it possible to identify individuals (i.e., one or more natural persons), either directly or indirectly (i.e., in combination with other data) from the dataset? If so, please describe how.   

Yes, individuals can potentially be identified through the combination of Res ID, address information (street number, street name, apartment), and date of birth. The unique Res ID serves as a direct identifier, and the address information could be used to locate specific individuals. This is why the dataset requires careful handling and should only be used for legitimate housing outreach purposes.   
* Dataset Snapshot, if there are multiple datasets please include multiple tables for each dataset. 


| Size of dataset |  |
| :---- | :---- |
| Number of instances | 43,759 total registered voters; 7,384 elderly residents (62+) |
| Number of fields  | 10 fields per instance |
| Labeled classes | N/A (demographic analysis, not classification) |
| Number of labels  | N/A |

**Primary Dataset: voter_list_cleaned.csv**
| Size of dataset |  |
| :---- | :---- |
| Number of instances | 43,759 |
| Number of fields  | 10 |
| Data types | String, Integer, Date |
| File size | ~2.5 MB |

**Derived Analysis Datasets:**
| Dataset | Instances | Fields | Purpose |
| :---- | :---- | :---- | :---- |
| ward_elderly_analysis.csv | 2 | 6 | Ward-level elderly statistics |
| precinct_elderly_analysis.csv | 31 | 4 | Precinct-level analysis |
| street_elderly_analysis.csv | 362 | 4 | Street-level analysis |  |


  
*Collection Process*

* What mechanisms or procedures were used to collect the data (e.g., API, artificially generated, crowdsourced \- paid, crowdsourced \- volunteer, scraped or crawled, survey, forms, or polls, taken from other existing datasets, provided by the client, etc)? How were these mechanisms or procedures validated?  

The data was provided directly by the client (ABCDC) and originates from the City of Boston's voter registration database. The data collection mechanism follows standard voter registration procedures where individuals register to vote through official channels (online, mail, or in-person). The data was validated through the City of Boston's official voter registration system and represents the authoritative record of registered voters in Wards 21 and 22.

* If the dataset is a sample from a larger set, what was the sampling strategy (e.g., deterministic, probabilistic with specific sampling probabilities)?  

This is not a sample dataset. It represents the complete voter registration database for Wards 21 and 22 of Boston. The dataset includes all registered voters in these specific geographic areas as of the data collection date.

* Over what timeframe was the data collected? Does this timeframe match the creation timeframe of the data associated with the instances (e.g., recent crawl of old news articles)? If not, please describe the timeframe in which the data associated with the instances was created. 

The dataset represents a snapshot of voter registration data as of the time it was provided by ABCDC (October 2025). The voter registration records themselves were created over time as individuals registered to vote, with dates of birth spanning from the early 1900s to the 2000s. The timeframe of data collection matches the timeframe of the instances, as voter registration is an ongoing process that captures current registered voters. 

*Preprocessing/cleaning/labeling* 

* Was any preprocessing/cleaning/labeling of the data done (e.g., discretization or bucketing, tokenization, part-of-speech tagging, SIFT feature extraction, removal of instances, processing of missing values)? If so, please provide a description. If not, you may skip the remaining questions in this section.   

Yes, significant preprocessing and cleaning was performed on the dataset:

1. **Column Selection:** The original Excel file contained additional fields that were not relevant to the housing analysis. Only 10 key fields were selected and retained.

2. **Data Type Standardization:** Date of birth fields were converted to proper datetime format for age calculations.

3. **Age Calculation:** Ages were calculated from date of birth to identify elderly residents (62+ years).

4. **Geographic Aggregation:** Data was aggregated at multiple levels (ward, precinct, street) for analysis.

5. **Statistical Analysis:** Mean and median ages were calculated for different geographic segments.

* Were any transformations applied to the data (e.g., cleaning mismatched values, cleaning missing values, converting data types, data aggregation, dimensionality reduction, joining input sources, redaction or anonymization, etc.)? If so, please provide a description.   

The following transformations were applied:

- **Data Type Conversion:** DOB fields converted from Excel date format to pandas datetime
- **Age Calculation:** Computed current age from date of birth for elderly identification
- **Geographic Aggregation:** Created summary statistics by ward, precinct, and street
- **Data Filtering:** Focused analysis on elderly population (62+ years)
- **Statistical Computations:** Calculated mean and median ages for demographic analysis
- **File Format Conversion:** Converted from Excel (.xls) to CSV format for easier processing

* Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data (e.g., to support unanticipated future uses)? If so, please provide a link or other access point to the "raw" data, this could be a link to a folder in your GitHub Repo, Spark\! owned Google Drive Folder for this project, or a path on the SCC, etc.  

Yes, the raw data is preserved in the project repository at: `fa25-team-a/data/raw/Voter List - Ward 21 and 22.xls`

* Is the code that was used to preprocess/clean the data available? If so, please provide a link to it (e.g., EDA notebook/EDA script in the GitHub repository). 

Yes, all preprocessing and analysis code is available in the project repository:

- **Data Cleaning Script:** `fa25-team-a/scripts/clean_voterList.py`
- **Geographic Analysis Script:** `fa25-team-a/scripts/geoanalysis_voterlist.py` 
- **EDA Notebook:** `fa25-team-a/notebooks/eda_voterList.ipynb`
- **Analysis Report:** `fa25-team-a/reports/EDA_VoterList_Analysis.md` 

*Uses* 

* What tasks has the dataset been used for so far? Please provide a description.   

The dataset has been used for the following tasks in this project:

1. **Demographic Analysis:** Identification and profiling of elderly residents (62+ years) in Allston-Brighton
2. **Geographic Analysis:** Mapping elderly population distribution across wards, precincts, and streets
3. **Housing Outreach Planning:** Identifying high-concentration areas for targeted affordable senior housing outreach
4. **Statistical Analysis:** Computing age distributions, mean/median ages, and population statistics
5. **Visualization:** Creating charts and graphs to illustrate demographic patterns and geographic distribution

* What (other) tasks could the dataset be used for?  

The dataset could potentially be used for:

1. **Voter Turnout Analysis:** Analyzing voting patterns by age group and geographic location
2. **Community Planning:** Informing decisions about senior services, transportation, and healthcare facilities
3. **Demographic Research:** Studying aging patterns and population trends in urban neighborhoods
4. **Public Health Planning:** Identifying areas with high elderly populations for health service planning
5. **Transportation Planning:** Understanding mobility needs of elderly residents by location
6. **Social Services Planning:** Targeting social services and community programs to areas with high elderly populations

* Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?   

Several factors may impact future uses:

1. **Limited Scope:** Dataset only includes registered voters, not the entire population
2. **Geographic Limitation:** Restricted to Wards 21 and 22 (Allston-Brighton only)
3. **Temporal Snapshot:** Represents a point-in-time view that may become outdated
4. **Occupation Data Quality:** High proportion of "UNKNOWN" occupation values limits economic analysis
5. **Privacy Considerations:** Contains personally identifiable information requiring careful handling

* Are there tasks for which the dataset should not be used? If so, please provide a description.

The dataset should NOT be used for:

1. **Commercial Marketing:** Personal information should not be used for commercial purposes
2. **Discriminatory Practices:** Should not be used to exclude or discriminate against any demographic groups
3. **Political Campaigning:** While voter data, it should not be used for partisan political activities
4. **Individual Targeting:** Should not be used to target specific individuals for any purpose
5. **Unauthorized Data Sharing:** Should not be shared with unauthorized parties or used beyond the stated housing outreach purpose

*Distribution*

* Based on discussions with the client, what access type should this dataset be given (eg., Internal (Restricted), External Open Access, Other)?

**Internal (Restricted)** - The dataset contains personally identifiable information including unique resident IDs, addresses, and dates of birth. Access should be restricted to authorized personnel involved in the ABCDC affordable senior housing initiative. The data should only be used for the specific purpose of identifying and reaching out to elderly residents for affordable housing opportunities. Any sharing or distribution should require explicit permission from ABCDC and should follow appropriate data privacy protocols.

*Maintenance* 

* If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so? If so, please provide a description.

Given the sensitive nature of the data and the specific purpose of the ABCDC affordable senior housing initiative, there is no general mechanism for external parties to extend or augment this dataset. Any extensions or contributions would need to:

1. **Obtain explicit permission** from ABCDC as the data owner
2. **Demonstrate legitimate need** related to affordable housing or senior services
3. **Follow strict privacy protocols** and data handling requirements
4. **Align with the original purpose** of identifying elderly residents for housing outreach
5. **Comply with applicable privacy laws** and regulations

The analysis code and methodology developed in this project (available in the repository) could potentially be adapted for similar analyses in other geographic areas, but would require separate data sources and appropriate permissions. 

*Other*

* Is there any other additional information that you would like to provide that has not already been covered in other sections?

**Additional Important Information:**

1. **Data Quality Assurance:** The dataset underwent thorough quality checks during the cleaning process, including validation of date formats, address standardization, and completeness verification.

2. **Geographic Context:** Wards 21 and 22 represent the Allston-Brighton neighborhood of Boston, which is a diverse area with significant student populations, long-term residents, and growing elderly communities.

3. **Methodological Notes:** The age threshold of 62+ years was chosen based on typical eligibility criteria for senior housing programs and represents a standard definition of "elderly" in housing policy contexts.

4. **Ethical Considerations:** This project was conducted with careful attention to privacy and ethical data use, focusing on community benefit and equitable housing access rather than individual targeting.

5. **Future Data Updates:** The dataset represents a snapshot in time and would benefit from periodic updates to reflect changes in voter registration, population shifts, and housing needs.

6. **Collaboration with ABCDC:** This analysis was conducted in close collaboration with ABCDC staff to ensure the results are actionable and aligned with their mission of providing affordable housing opportunities for seniors in Allston-Brighton.

