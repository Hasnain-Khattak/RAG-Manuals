from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
import os, dotenv
import shutil
import sqlite3
#import fitz  # PyMuPDF for image extraction
    #import pymupdf
    # or
import pymupdf as fitz
import io
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import time

load_dotenv()

#os.environ['OPNEAI_API_KEY'] = "API-KEY"
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

client = OpenAI()
# Define paths
DATA_PATHS = [
    ["./Data/A6_039BD5B2D0EBF.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/289/A6_039BD5B2D0EBF.pdf"],
    ["./Data/After_DarkDLX__A105__20121208_7A019C06B663E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/125/After_DarkDLX__A105__20121208_7A019C06B663E.pdf"],
    ["./Data/After_DarkSTD__A107_GMPDELL_PC20134_03BD8DE985B79.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/122/After_DarkSTD__A107_GMPDELL_PC20134_03BD8DE985B79.pdf"],
    ["./Data/Angel_Carousel_CE65D58E57815.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/32/Angel_Carousel_CE65D58E57815.pdf"],
    ["./Data/Arka_Manual_1_C129EACEF2AAE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/128/Arka_Manual_1_C129EACEF2AAE.pdf"],
    ["./Data/Astro_Invasion_GMP__A108__manual_20_9F9B71CC59F8E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/131/Astro_Invasion_GMP__A108__manual_20_9F9B71CC59F8E.pdf"],
    ["./Data/B145__Bigfoot_Mayhem_GMP_65_Manual__489C777586E19.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/376/B145__Bigfoot_Mayhem_GMP_65_Manual__489C777586E19.pdf"],
    ["./Data/B148__Bigfoot_Smash_Manual_GMP_1114_87E4DBCFAC0D8.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/423/B148__Bigfoot_Smash_Manual_GMP_1114_87E4DBCFAC0D8.pdf"],
    ["./Data/Barrel_of_laughs_manual_2017418__7E114A76FD775.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/134/Barrel_of_laughs_manual_2017418__7E114A76FD775.pdf"],
    ["./Data/BasketballEliteManual2020_6DA49D72C60BC.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/267/BasketballEliteManual2020_6DA49D72C60BC.pdf"],
    ["./Data/Beat_the_goalie_manual_Rev1_0A2B725519EB5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/137/Beat_the_goalie_manual_Rev1_0A2B725519EB5.pdf"],
    ["./Data/bigfootflyer_new_letter_copy_7E5B6AE48910F.pdf", "https://www.unispartsandservice.com/media/cms/bigfootflyer_new_letter_copy_7E5B6AE48910F.pdf"],
    ["./Data/Big_Foot_Crush_GMP_Manual_2020_CC8EEAC4A5EAE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/280/Big_Foot_Crush_GMP_Manual_2020_CC8EEAC4A5EAE.pdf"],
    ["./Data/bike_rally_GMP_manual2017822_90B4B290AD5EA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/140/bike_rally_GMP_manual2017822_90B4B290AD5EA.pdf"],
    ["./Data/Bowl_Master_Manual2019_B69BC2C58A520.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/7/Bowl_Master_Manual2019_B69BC2C58A520.pdf"],
    ["./Data/Bunny_Pond_Manual_2014926_76D40D002278F.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/143/Bunny_Pond_Manual_2014926_76D40D002278F.pdf"],
    ["./Data/cargo_express_manual_2019_D799C4DEE1DD5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/146/cargo_express_manual_2019_D799C4DEE1DD5.pdf"],
    ["./Data/CheekyMonkey_Football_Manual_2_322D32929231F.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/147/CheekyMonkey_Football_Manual_2_322D32929231F.pdf"],
    ["./Data/Circle_Train_CEC_manual__201768_F222BCA17A7CB.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/150/Circle_Train_CEC_manual__201768_F222BCA17A7CB.pdf"],
    ["./Data/Coconut_Bash_GMP_20190607_03C9D066D0BDC.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/66/Coconut_Bash_GMP_20190607_03C9D066D0BDC.pdf"],
    ["./Data/Cowboy_Shootout_V1_C917D367C5CE1.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/407/Cowboy_Shootout_V1_C917D367C5CE1.pdf"],
    ["./Data/Crazy_Hoop_manual_2_EAECDD679CDEE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/153/Crazy_Hoop_manual_2_EAECDD679CDEE.pdf"],
    ["./Data/D121__Duo_Drive_Manual_3ED3ED058ED70.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/35/D121__Duo_Drive_Manual_3ED3ED058ED70.pdf"],
    ["./Data/D158__Derby_Champion_Club_GMP_Manua_A19AEF6CA6C13.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/321/D158__Derby_Champion_Club_GMP_Manua_A19AEF6CA6C13.pdf"],
    ["./Data/D175__Ducky_Splash_3_GMP_Manual_202_570FF80052C50.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/399/D175__Ducky_Splash_3_GMP_Manual_202_570FF80052C50.pdf"],
    ["./Data/D177__Duck_Party_GMP_Manual_SKNJ090_BCA0680B42FD0.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/402/D177__Duck_Party_GMP_Manual_SKNJ090_BCA0680B42FD0.pdf"],
    ["./Data/Derby_champions_GMP_ManualBrown_hor_DBD5735065ED2.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/156/Derby_champions_GMP_ManualBrown_hor_DBD5735065ED2.pdf"],
    ["./Data/Derby_champions_GMP_ManualWhite_hor_F7D30F6B89AC5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/254/Derby_champions_GMP_ManualWhite_hor_F7D30F6B89AC5.pdf"],
    ["./Data/DinoPopManualAW20110516_E1CB45FB27527.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/158/DinoPopManualAW20110516_E1CB45FB27527.pdf"],
    ["./Data/Disc_it_for_Tickets_Twin_Version__M_7E2210B4A2F5D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/257/Disc_it_for_Tickets_Twin_Version__M_7E2210B4A2F5D.pdf"],
    ["./Data/Disc_it_Single_GMP_Manual_20191115_E323550199CAB.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/260/Disc_it_Single_GMP_Manual_20191115_E323550199CAB.pdf"],
    ["./Data/Dizzy_Lizzy_1P_GMP_Manual_201949_6E1E64788F478.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/18/Dizzy_Lizzy_1P_GMP_Manual_201949_6E1E64788F478.pdf"],
    ["./Data/Dizzy_Lizzy_3P_GMP_Manual_201949_F774797CA876E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/263/Dizzy_Lizzy_3P_GMP_Manual_201949_F774797CA876E.pdf"],
    ["./Data/Drummer_Kids_manual20141010_B8A4074EACD0C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/161/Drummer_Kids_manual20141010_B8A4074EACD0C.pdf"],
    ["./Data/Ducky_splash_manual_D114_GMP_DFF9EDCD5C30B.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/23/Ducky_splash_manual_D114_GMP_DFF9EDCD5C30B.pdf"],
    ["./Data/E108__Extreme_Shot_Operation_Manual_3F823DEBBB9B5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/335/E108__Extreme_Shot_Operation_Manual_3F823DEBBB9B5.pdf"],
    ["./Data/E120_Emoji_Frenzy_DB_Manual_2023_F4D579C314943.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/357/E120_Emoji_Frenzy_DB_Manual_2023_F4D579C314943.pdf"],
    ["./Data/E124_Emoji_Frenzy_GMP_Manual_2023_677209AD64CC1.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/406/E124_Emoji_Frenzy_GMP_Manual_2023_677209AD64CC1.pdf"],
    ["./Data/Elevator_Action_Invasion_DB_Manual__8C8995DEFAF4A.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/291/Elevator_Action_Invasion_DB_Manual__8C8995DEFAF4A.pdf"],
    ["./Data/Elevator_Action_Invasion_DB_Manual__C89932D31604A.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/299/Elevator_Action_Invasion_DB_Manual__C89932D31604A.pdf"],
    ["./Data/Emoji_Roller_GMP_Manual_2022917_14F9ACE93EF28.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/333/Emoji_Roller_GMP_Manual_2022917_14F9ACE93EF28.pdf"],
    ["./Data/Extreme_Hoops_Operation_Manual_2014_24DE1C2C20FC5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/29/Extreme_Hoops_Operation_Manual_2014_24DE1C2C20FC5.pdf"],
    ["./Data/F132__Frost_Island_manual_rev1_C299FCA62621D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/364/F132__Frost_Island_manual_rev1_C299FCA62621D.pdf"],
    ["./Data/F160__Fantastic_Prize_GMP_Skill_202_983CAE1BD3381.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/309/F160__Fantastic_Prize_GMP_Skill_202_983CAE1BD3381.pdf"],
    ["./Data/F164_Skill_Fantastic_Prize_2_Black__396272AA54DBF.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/370/F164_Skill_Fantastic_Prize_2_Black__396272AA54DBF.pdf"],
    ["./Data/F165_Skill_Fantastic_Prize_2_Blue_G_000FFE816AC7D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/367/F165_Skill_Fantastic_Prize_2_Blue_G_000FFE816AC7D.pdf"],
    ["./Data/F168__Funko_Funcade_GMP_Manual_2024_3FB90188A2EAE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/418/F168__Funko_Funcade_GMP_Manual_2024_3FB90188A2EAE.pdf"],
    ["./Data/Fantasy_Soccer_Manual_GMP_2019_AEC2D541E3EC6.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/60/Fantasy_Soccer_Manual_GMP_2019_AEC2D541E3EC6.pdf"],
    ["./Data/FireRescue_manual_Revised_E7AF89583AB1C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/78/FireRescue_manual_Revised_E7AF89583AB1C.pdf"],
    ["./Data/Fruit_Mania_DLX_Manual_2272013_6A0BF56BF30FA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/332/Fruit_Mania_DLX_Manual_2272013_6A0BF56BF30FA.pdf"],
    ["./Data/Fruit_Mania_STD_Manual_2272013_6E9DFD3361854.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/329/Fruit_Mania_STD_Manual_2272013_6E9DFD3361854.pdf"],
    ["./Data/Fun_Fair_Bash_Manua_l2013730_A79FEA9B31C55.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/325/Fun_Fair_Bash_Manua_l2013730_A79FEA9B31C55.pdf"],
    ["./Data/G130__GvK_Smasher_4P_Manual_2024_0BC8C4C9E0F1E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/386/G130__GvK_Smasher_4P_Manual_2024_0BC8C4C9E0F1E.pdf"],
    ["./Data/G131_110V_GvK_Smasher_2P_GMP_Manual_D9AD5A7FED807.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/389/G131_110V_GvK_Smasher_2P_GMP_Manual_D9AD5A7FED807.pdf"],
    ["./Data/Game_Update_Instruction_For_Elite_B_EE2D9ECB09277.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/272/Game_Update_Instruction_For_Elite_B_EE2D9ECB09277.pdf"],
    ["./Data/ghostHunter071010_C104EF24BF3E6.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/164/ghostHunter071010_C104EF24BF3E6.pdf"],
    ["./Data/Hammer_FroggieGMPver2019_78FFDE72BD453.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/167/Hammer_FroggieGMPver2019_78FFDE72BD453.pdf"],
    ["./Data/Hammer_Fun_Manual_6182013H106__FFAFB1788902D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/170/Hammer_Fun_Manual_6182013H106__FFAFB1788902D.pdf"],
    ["./Data/How_to_set_the_wireless_password_BDD8E409062EE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/275/How_to_set_the_wireless_password_BDD8E409062EE.pdf"],
    ["./Data/Instructionofconvertingticketdomefr_543105D7BBC1C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/251/Instructionofconvertingticketdomefr_543105D7BBC1C.pdf"],
    ["./Data/JackMechanismErrorInspectionInstruc_0822A0A2366E3.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/117/JackMechanismErrorInspectionInstruc_0822A0A2366E3.pdf"],
    ["./Data/Jetball_Ads_0F1D96EE9A67C.pdf", "https://www.unispartsandservice.com/media/cms/Jetball_Ads_0F1D96EE9A67C.pdf"],
    ["./Data/Jetball_Alley_2P_GMPG4K_Manual_2021_F377FB569B794.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/296/Jetball_Alley_2P_GMPG4K_Manual_2021_F377FB569B794.pdf"],
    ["./Data/Jetball_Alley_Single_GMPG4K_Manual__B0242C5D90A0C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/173/Jetball_Alley_Single_GMPG4K_Manual__B0242C5D90A0C.pdf"],
    ["./Data/L105__Lane_Master_GMP_1172018_Newes_794375C469EB6.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/10/L105__Lane_Master_GMP_1172018_Newes_794375C469EB6.pdf"],
    ["./Data/L110_Lane_Master_DB_Manual_2017_10__80439583C4BFE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/96/L110_Lane_Master_DB_Manual_2017_10__80439583C4BFE.pdf"],
    ["./Data/L129__Lane_Master_Xtreme_GMP_12_F40D6F854D6E0.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/379/L129__Lane_Master_Xtreme_GMP_12_F40D6F854D6E0.pdf"],
    ["./Data/L130__Lane_Master_Xtreme_GMPTickets_E5B52F4BE50C8.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/378/L130__Lane_Master_Xtreme_GMPTickets_E5B52F4BE50C8.pdf"],
    ["./Data/Lane_Master_Pro_Manual_GMP_2020_0EF6022624F78.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/100/Lane_Master_Pro_Manual_GMP_2020_0EF6022624F78.pdf"],
    ["./Data/M149__Fantastic_Prize_Mini_1P_110V__F876DAB04A5CC.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/381/M149__Fantastic_Prize_Mini_1P_110V__F876DAB04A5CC.pdf"],
    ["./Data/Mini_Police_Ride_manual_11_06_1DF12813AFB49.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/179/Mini_Police_Ride_manual_11_06_1DF12813AFB49.pdf"],
    ["./Data/Mini_PONG_BOM_for_Gene_202098_75D9BC5A71814.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/283/Mini_PONG_BOM_for_Gene_202098_75D9BC5A71814.pdf"],
    ["./Data/Mini_TrainsmokeGMP_ver_manual2014_0EE124A833076.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/182/Mini_TrainsmokeGMP_ver_manual2014_0EE124A833076.pdf"],
    ["./Data/Night_Hunter_Manual_2019_6C87D877FA59D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/93/Night_Hunter_Manual_2019_6C87D877FA59D.pdf"],
    ["./Data/O119_Over_The_Edge_Plus_GMP_Manual__F645652E8DAEE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/351/O119_Over_The_Edge_Plus_GMP_Manual__F645652E8DAEE.pdf"],
    ["./Data/O120__Over_The_Edge_Single_Manual_0_0D62FC6FBD393.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/403/O120__Over_The_Edge_Single_Manual_0_0D62FC6FBD393.pdf"],
    ["./Data/OctonautsCaptain_Barnacles_GMP_Manu_D8B324AE8373D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/318/OctonautsCaptain_Barnacles_GMP_Manu_D8B324AE8373D.pdf"],
    ["./Data/OctonautsKwazii_GMP_Manual_2022_FE83F716256A0.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/315/OctonautsKwazii_GMP_Manual_2022_FE83F716256A0.pdf"],
    ["./Data/OctonautsPeso_GMP_Manual_2022_FEAF7CC170B4A.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/312/OctonautsPeso_GMP_Manual_2022_FEAF7CC170B4A.pdf"],
    ["./Data/P126__Pirates_Hook_1P_tprize_ver__2_21AB74E8BD995.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/198/P126__Pirates_Hook_1P_tprize_ver__2_21AB74E8BD995.pdf"],
    ["./Data/P167__Power_Puck_Fever_GMP_Manual_3_EC878472FCB42.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/342/P167__Power_Puck_Fever_GMP_Manual_3_EC878472FCB42.pdf"],
    ["./Data/P171__Prize_Catcher_GMP_Manual_2024_3F4E04685E2BE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/415/P171__Prize_Catcher_GMP_Manual_2024_3F4E04685E2BE.pdf"],
    ["./Data/Panning_for_gold_ticket_manualGMP20_A02CDF13AF169.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/38/Panning_for_gold_ticket_manualGMP20_A02CDF13AF169.pdf"],
    ["./Data/Penguin_Slope_Manual_GMP_2018_119FFA3FB97D5.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/188/Penguin_Slope_Manual_GMP_2018_119FFA3FB97D5.pdf"],
    ["./Data/Photo_RideCEC_manual_2013917_F37F0C9F0C082.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/192/Photo_RideCEC_manual_2013917_F37F0C9F0C082.pdf"],
    ["./Data/Pin_setter_2P_GMP_BOM_2018_0692A894E02C7.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/195/Pin_setter_2P_GMP_BOM_2018_0692A894E02C7.pdf"],
    ["./Data/Pin_setter_2P_GMP_BOM_2018_74206DF39C55D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/90/Pin_setter_2P_GMP_BOM_2018_74206DF39C55D.pdf"],
    ["./Data/Pirates_Hook_4P_GMP_Manual2019625_B074560B02CBA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/44/Pirates_Hook_4P_GMP_Manual2019625_B074560B02CBA.pdf"],
    ["./Data/Pogo_Jump_DLX_GMP_Manual_2022_E22D5E48725AF.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/322/Pogo_Jump_DLX_GMP_Manual_2022_E22D5E48725AF.pdf"],
    ["./Data/Polar_Igloo_manual_GMP_2018510_FD1F67C7C1802.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/207/Polar_Igloo_manual_GMP_2018510_FD1F67C7C1802.pdf"],
    ["./Data/PONG_1_4C8D69EAEA8C6.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/15/PONG_1_4C8D69EAEA8C6.pdf"],
    ["./Data/PONG_4P_DB_Manual_2019_795E3136A15DE.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/338/PONG_4P_DB_Manual_2019_795E3136A15DE.pdf"],
    ["./Data/PONG_arcade_manual_20190813_7EECF03AA5C80.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/75/PONG_arcade_manual_20190813_7EECF03AA5C80.pdf"],
    ["./Data/PONG_cocktail_manual_20190813_522E285304A7D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/72/PONG_cocktail_manual_20190813_522E285304A7D.pdf"],
    ["./Data/R134_Raccon_Rampage_GMP_2023_2EA179F7E43CD.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/373/R134_Raccon_Rampage_GMP_2023_2EA179F7E43CD.pdf"],
    ["./Data/Racing_Jet_manual_20151027_2_AEC07344A0B74.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/210/Racing_Jet_manual_20151027_2_AEC07344A0B74.pdf"],
    ["./Data/Rocket_School_Bus_GMP_monitor_verma_C3D30A663090C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/213/Rocket_School_Bus_GMP_monitor_verma_C3D30A663090C.pdf"],
    ["./Data/S117__Squirt_a_gator2014628_23B0DC2D2101F.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/326/S117__Squirt_a_gator2014628_23B0DC2D2101F.pdf"],
    ["./Data/S123__Safari_Ranger_2P_manual201569_3366029B27B5A.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/222/S123__Safari_Ranger_2P_manual201569_3366029B27B5A.pdf"],
    ["./Data/S124__Safari_Ranger4P_manual2014102_35A40D9358337.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/101/S124__Safari_Ranger4P_manual2014102_35A40D9358337.pdf"],
    ["./Data/S132__ski_racer_manual_2015815_B8427585E883E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/228/S132__ski_racer_manual_2015815_B8427585E883E.pdf"],
    ["./Data/S135__Safari_Ranger_1P_prize_ver____95DA1032A92F7.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/216/S135__Safari_Ranger_1P_prize_ver____95DA1032A92F7.pdf"],
    ["./Data/S138__Strike_pro_Fishing_manual_Rev_F5441E6A89CD6.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/237/S138__Strike_pro_Fishing_manual_Rev_F5441E6A89CD6.pdf"],
    ["./Data/S185__Sailors_Quest_VR_Manual_31620_072D77B9705B4.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/340/S185__Sailors_Quest_VR_Manual_31620_072D77B9705B4.pdf"],
    ["./Data/S187__Space_Raider_GMP_Manual_36202_C9A6F0953342A.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/345/S187__Space_Raider_GMP_Manual_36202_C9A6F0953342A.pdf"],
    ["./Data/Safari_Ranger_1P_ticket__manual_9CDBC90469763.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/219/Safari_Ranger_1P_ticket__manual_9CDBC90469763.pdf"],
    ["./Data/Saucer_Manual_CEC_Rev1_0_2011430_87E7794797E34.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/225/Saucer_Manual_CEC_Rev1_0_2011430_87E7794797E34.pdf"],
    ["./Data/Seaway_submarine_manual_201469_167C632D55D2E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/87/Seaway_submarine_manual_201469_167C632D55D2E.pdf"],
    ["./Data/Skill_Grand_Prize_GMP_Manual_2023_C62874C6BBB7F.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/361/Skill_Grand_Prize_GMP_Manual_2023_C62874C6BBB7F.pdf"],
    ["./Data/Skill_Grand_Prize_GMP_XL_Manual_202_EC161E7828473.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/363/Skill_Grand_Prize_GMP_XL_Manual_202_EC161E7828473.pdf"],
    ["./Data/SKNJ_Toy_Box_LCD_GMP_Manual_2024_0CC8018B35513.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/398/SKNJ_Toy_Box_LCD_GMP_Manual_2024_0CC8018B35513.pdf"],
    ["./Data/SKNJ_Toy_Box_Single_GMP_Manual_2024_C2D39CE0B3A58.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/395/SKNJ_Toy_Box_Single_GMP_Manual_2024_C2D39CE0B3A58.pdf"],
    ["./Data/SpaceshipGMP_manual_2019126_997DA1110AD8E.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/231/SpaceshipGMP_manual_2019126_997DA1110AD8E.pdf"],
    ["./Data/Speedy_feet_GMP_Manual_2019_F3AF1331A9107.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/234/Speedy_feet_GMP_Manual_2019_F3AF1331A9107.pdf"],
    ["./Data/Star_Crusaders_2_GMP_Manual_2022_24031279ABDF9.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/348/Star_Crusaders_2_GMP_Manual_2022_24031279ABDF9.pdf"],
    ["./Data/Super_big_rig_manual_201574__B4CDB8A6776BD.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/84/Super_big_rig_manual_201574__B4CDB8A6776BD.pdf"],
    ["./Data/System_Update_Recovery_Instruction__C86F097B8E991.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/276/System_Update_Recovery_Instruction__C86F097B8E991.pdf"],
    ["./Data/T106__Tiger_Bowl_Manual_8DBA90B5CCE25.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/240/T106__Tiger_Bowl_Manual_8DBA90B5CCE25.pdf"],
    ["./Data/T120__Toss_Up_manual_20131219_2_643093996DC49.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/243/T120__Toss_Up_manual_20131219_2_643093996DC49.pdf"],
    ["./Data/T155__To_Tha_Net_Low_Profile_GMPGol_BBDE1F68BB050.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/350/T155__To_Tha_Net_Low_Profile_GMPGol_BBDE1F68BB050.pdf"],
    ["./Data/T164__Time_Out_GMP_Manual_2023_8D0EAE333CF17.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/383/T164__Time_Out_GMP_Manual_110V_0531_9DCE1E7A63329.pdf"],
    ["./Data/T167_SKNJ_Toy_Box_2P_GMP_Manual_202_EEA4CE69CDB9D.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/412/T167_SKNJ_Toy_Box_2P_GMP_Manual_202_EEA4CE69CDB9D.pdf"],
    ["./Data/T169__SKNJ_Toy_Box_4P_Mini_GMP_Manu_E395D1D15B707.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/392/T169__SKNJ_Toy_Box_4P_Mini_GMP_Manu_E395D1D15B707.pdf"],
    ["./Data/T170_Toy_Box_XL_GMP_Manual_2023_3E39A08BAA051.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/409/T170_Toy_Box_XL_GMP_Manual_2023_3E39A08BAA051.pdf"],
    ["./Data/T175__Toy_Box_FlatTop_Manual_GMP_12_9721CA017FDC7.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/421/T175__Toy_Box_FlatTop_Manual_GMP_12_9721CA017FDC7.pdf"],
    ["./Data/Ticket_Dome_Poster_703A7B5774369.pdf", "https://www.unispartsandservice.com/media/cms/Ticket_Dome_Poster_703A7B5774369.pdf"],
    ["./Data/Ticket_Dome_RFID__manual__2022416_5563D4DF71093.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/120/Ticket_Dome_RFID__manual__2022416_5563D4DF71093.pdf"],
    ["./Data/ToThaNetcombo_F4F068E42D678.pdf", "https://www.unispartsandservice.com/media/cms/ToThaNetcombo_F4F068E42D678.pdf"],
    ["./Data/To_Tha_Net_GMP_Manual_2019_8EC5E9534E85F.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/108/To_Tha_Net_GMP_Manual_2019_8EC5E9534E85F.pdf"],
    ["./Data/To_Tha_Net_JR_2629DE3E83132.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/114/To_Tha_Net_JR_2629DE3E83132.pdf"],
    ["./Data/Treasure_cove_1LT75BN21_Screen_Fix_F698BDA924366.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/265/Treasure_cove_1LT75BN21_Screen_Fix_F698BDA924366.pdf"],
    ["./Data/Treasure_Cove_Manual_20190829_01FB80D112330.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/48/Treasure_Cove_Manual_20190829_01FB80D112330.pdf"],
    ["./Data/Treasure_Dome_GMP_manual_2019413_45278559271CC.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/54/Treasure_Dome_GMP_manual_2019413_45278559271CC.pdf"],
    ["./Data/Tubin_Twist_Manual_GMP_201684_50CE4367BEA13.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/246/Tubin_Twist_Manual_GMP_201684_50CE4367BEA13.pdf"],
    ["./Data/U103__Up_and_Away_Manual_Updating_7784501DEA242.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/249/U103__Up_and_Away_Manual_Updating_7784501DEA242.pdf"],
    ["./Data/Ultra_Moto_VR_Flyer_5A5D1EFFC4EF2.pdf", "https://www.unispartsandservice.com/media/cms/Ultra_Moto_VR_Flyer_5A5D1EFFC4EF2.pdf"],
    ["./Data/Ultra_Moto_VR_Manual_2020_4A5609443886B.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/105/Ultra_Moto_VR_Manual_2020_4A5609443886B.pdf"],
    ["./Data/UnisEliteTrampolineGamesManual20205_DAFB9931F83A0.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/270/UnisEliteTrampolineGamesManual20205_DAFB9931F83A0.pdf"],
    ["./Data/Unis_Elite_Trampoline_Games_Manual__426A6D4002BFA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/286/Unis_Elite_Trampoline_Games_Manual__426A6D4002BFA.pdf"],
    ["./Data/W122__Wicked_Tuna_2P_GMP_Manual_202_38F7BCF6E16DA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/308/W122__Wicked_Tuna_2P_GMP_Manual_202_38F7BCF6E16DA.pdf"],
    ["./Data/Wicked_Tuna_DB_Manual_2022_D40A005E46A64.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/301/Wicked_Tuna_DB_Manual_2022_D40A005E46A64.pdf"],
    ["./Data/WiFi_Antenna_Installation_Instructi_19D1A7642B98B.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/278/WiFi_Antenna_Installation_Instructi_19D1A7642B98B.pdf"],
    ["./Data/Work_Zone_GMP_Manual_2022_59CE52E3391EA.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/358/Work_Zone_GMP_Manual_2022_59CE52E3391EA.pdf"],
    ["./Data/World_Soccer_Manual_DB_2019_238AA28E34C8C.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/111/World_Soccer_Manual_DB_2019_238AA28E34C8C.pdf"],
    ["./Data/X109__Pirates_Hook_manual_LATEST_MA_8B5D249F7FBD0.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/201/X109__Pirates_Hook_manual_LATEST_MA_8B5D249F7FBD0.pdf"],
    ["./Data/ZombieNightGMPManual2020_D51952F1E3289.pdf", "https://www.unispartsandservice.com/moduledocuments/embed/102/ZombieNightGMPManual2020_D51952F1E3289.pdf"]
]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, "db", "updated-db")
IMAGE_DB_PATH = os.path.join(CURRENT_DIR, "db", "images.db")

def initialize_database():
    """Initialize SQLite database with proper permissions"""
    try:
        # Ensure directory exists
        db_dir = os.path.dirname(IMAGE_DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        
        # Set directory permissions (777 for development, adjust for production)
        os.chmod(db_dir, 0o777)
        
        # If database exists, set proper permissions
        if os.path.exists(IMAGE_DB_PATH):
            os.chmod(IMAGE_DB_PATH, 0o666)
        else:
            # Create new database file with proper permissions
            open(IMAGE_DB_PATH, 'a').close()
            os.chmod(IMAGE_DB_PATH, 0o666)
        
        # Create database connection
        conn = sqlite3.connect(IMAGE_DB_PATH)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_name TEXT,
                page_num INTEGER,
                image BLOB,
                pdf_link TEXT
            )
        """)
        conn.commit()
        return conn, cursor
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()
        raise

print(f"Current directory: {CURRENT_DIR}")
print(f"Database directory path: {DATABASE_DIR}")


import fitz  # PyMuPDF
import os
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



def pageDescription(manual_name, page, image):
    base64_image = encode_image(image)
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": f'''
                This is a page about the manual from {manual_name}, at page {page}. Give me a description of the page so that I may retrieve it from a vector database efficiently later. Your response must include the games name, the page number, and a description of the contents of the page.
               '''},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
              },
            },
          ],
        }
      ],
      max_tokens=4096,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content





def pdf_to_pngs(pdf_path, cleanName, output_folder="output", dpi=300):
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path[0])
        pages = []
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Convert each page to PNG with a white background
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=fitz.csRGB)  # Set resolution
            pix.save(os.path.join(output_folder, f"{cleanName}_page_{page_num+1}.png"))
            pngpath = os.path.join(output_folder, f"{cleanName}_page_{page_num+1}.png")
            print(f"Saved {os.path.join(output_folder, f'{cleanName}_page_{page_num+1}.png')}")
            pages.append(pngpath)
        
        pdf_document.close()
        return pages
    
    except Exception as e:
        return f"Error: {str(e)}"


def cleanText(filename):
 completion = client.chat.completions.create(
   model="gpt-4o-mini",
   messages=[
     {"role": "system", "content": "You are text cleaner agent. You take the name of a file and clean it so the returned text only has the name of the game and the and term 'Manual'. Exclude all other random characters and numbers in the return text."},
     {"role": "user", "content": "Godzilla_Kaiju_Wars_VR_Manual.pdf"},
     {"role": "assistant", "content": "Godzilla Kaiju Wars VR Manual"},
     {"role": "user", "content": "20200910_ON_POINT_SERVICE_Manual_En_2CA123513967E.pdf"},
     {"role": "assistant", "content": "On Point Service Manual"},
     {"role": "user", "content": f"{filename}"},
   ]
 )
 result = completion.choices[0].message.content
 print(completion.choices[0].message.content)
 return result

def image_to_bytes(image_path):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if it's in a different mode (e.g., RGBA)
            img = img.convert("RGB")
            # Create a bytes buffer
            byte_io = io.BytesIO()
            # Save the image to the buffer in PNG format
            img.save(byte_io, format="PNG")
            # Get the byte data
            byte_data = byte_io.getvalue()
            return byte_data
    except Exception as e:
        return f"Error: {str(e)}"

# # Connect to SQLite and create image table
# with sqlite3.connect(IMAGE_DB_PATH) as conn:
    # cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS images (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             pdf_name TEXT,
#             page_num INTEGER,
#             image BLOB,
#             pdf_link TEXT
#             )
#     """)
    # conn.commit()



def store_images_from_pdf(pdf_path, cleanName):
    """Extracts and stores images from a PDF into SQLite."""
    print("STORING IMAGES FROM PDF")
    doc = fitz.open(pdf_path[0])
    pdf_name = os.path.basename(pdf_path[0])
    pages = pdf_to_pngs(pdf_path, cleanName)
    
    conn = None
    conn, cursor = initialize_database()
    #for index, page_num in enumerate(range(len(doc))):
    for index, page in enumerate(pages):
            link = pdf_path[1]
            # NEED TO ADD DESCRIPTION of page
        #for img in doc[page_num].get_images(full=True):
            #print(f" the current page of the document is - {img}, xref is {img[0]}")
            #xref = img[0]
            #base_image = doc.extract_image(xref)
            #image_bytes = base_image["image"]
            image_bytes = image_to_bytes(pages[index])
            page_num = index
            print(f"INSERT INTO images pdf_name {pdf_name}, page_num {index}, image ")
            cursor.execute("INSERT INTO images (pdf_name, page_num, image, pdf_link) VALUES (?, ?, ?, ?)",
                           (cleanName, page_num, image_bytes, link))
            conn.commit()

def create_vector_store():
    print(f"""Creates a FAISS vector database from the given PDF documents.""")
    try:
        print("Creating vector store...")
        os.makedirs(DATABASE_DIR, exist_ok=True)

        documents = []
        for pdf_path in DATA_PATHS:
            print(f"CURRENT PDF PATH IS {pdf_path[0]}")
            loader = PyPDFLoader(pdf_path[0])
            docs = loader.load()
            cleanName = cleanText(os.path.basename(pdf_path[0]))
            print(f"ABOUT TO LOOP THROUGH DOCS IN {cleanName}")
            time.sleep(5)
            # Add metadata (file name & page number)
            for doc in docs:
                doc.metadata["source"] = cleanName
                #os.path.basename(pdf_path)  # Store filename
                doc.metadata["page"] = doc.metadata.get("page", "N/A")  # Store page number
                

            documents.extend(docs)
            #store_images_from_pdf(pdf_path)
            store_images_from_pdf(pdf_path, cleanName)  # Extract and store images

        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_docs = text_splitter.split_documents(documents)

        # Add more specific page range information to each chunk
        for doc in split_docs:
            doc.metadata["page_start"] = doc.metadata.get("page", 0)
            doc.metadata["page_end"] = doc.metadata.get("page", 0)

        # Create vector store
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large",)
        vector_store = FAISS.from_documents(split_docs, embedding=embeddings)
        print(f"About to save vector store to: {DATABASE_DIR}")
        vector_store.save_local(DATABASE_DIR)

        print("✅ Vector store and image storage completed successfully!")
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")

interactive = os.environ.get("INTERACTIVE_MODE", "true").lower() == "true"
# Main execution logic
if __name__ == "__main__":
    if not os.path.exists(DATABASE_DIR):
        print("Database does not exist. Initializing vector store...")
        create_vector_store()
    else:
        if interactive:
            user_input = input("Vector store already exists. Do you want to recreate the vector database? (yes/no): ").strip().lower()
            if user_input == "yes":
                shutil.rmtree(DATABASE_DIR)
                if os.path.exists(IMAGE_DB_PATH):
                    os.remove(IMAGE_DB_PATH)
                create_vector_store()
            else:
                print("Using existing vector store.")
        else:
           shutil.rmtree(DATABASE_DIR)
           if os.path.exists(IMAGE_DB_PATH):
                os.remove(IMAGE_DB_PATH)
                create_vector_store()

# Close SQLite connection
#conn.close()
