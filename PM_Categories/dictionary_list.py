#10112918 -Apple
#10920229 -Microsoft Surface
#10367579 -Lenovo PCG|DCG
#10940320 -Intel
#10466196 -Microsoft OS
#10016589 -AMD
#10357882 -Adobe
#10986883 -Barco
#10798467 -Net App
#10274175 -Samsung
#10278736 -Cisco

sr_tables={
           '10112918':
                {'cto_flag':True,
                  'cto_str_proc':"""
			          DECLARE @Sr_sold_to nvarchar(10)='10112918';
                          SELECT        
								         [key]=m.[SR_Sold_To] +'|'+ m.material
                                        ,[sr_soldto]=m.SR_Sold_To
				                        ,m.material
				                        ,[material_type]= 'internal_part_cto_result'
				                        ,[partner_category1]= p.[partner_category1]
				                        ,[partner_category2]= p.[partner_category2]
				                        ,[partner_category3]= p.[partner_category3]
				                        ,[partner_category4]= p.[partner_category4]
                                        ,[partner_category5]= p.[partner_category5]
                                        ,[partner_category6]= p.[partner_category6]
				                        ,[Partner_Price]= p.[Partner_Price]
				                        ,[sender]= p.[sender]
				                        ,[append_date]=p.[append_date]
                                        ,[Material_Rebate]=p.[Material_Rebate]
	                     INTO ##PM_cat_temp
                 
				         FROM 
					        [marketing_work].[pm_na].[pm_categories_prd] AS p

			         LEFT JOIN 
					        [marketing_prod].[dbo].[prod_material] AS m ON LEFT(m.material,4)=p.material and p.SR_SoldTo=m.SR_Sold_To

			          WHERE 
					         p.SR_SoldTo = @Sr_sold_to
					         AND p.Material_type='internal_part_cto'

              """
             ,'analyst':'yunior.rosellruiz@insight'}
          ,'10367579':
                {'cto_flag':True,
                  'cto_str_proc':"""                
					DECLARE @Sr_sold_to NVARCHAR(10)='10367579';

	                SELECT DISTINCT
				                 [key]=m.[SR_Sold_To] +'|'+ m.material
                                ,[sr_soldto]=COALESCE(p.[sr_soldto],pc.[sr_soldto],m.SR_Sold_To)
				                ,m.material
				                ,[material_type]= COALESCE (p.[material_type],pc.[material_type],'internal_part')
				                ,[partner_category1]= COALESCE (p.[partner_category1],pc.[partner_category1])
				                ,[partner_category2]= COALESCE (p.[partner_category2],pc.[partner_category2])
				                ,[partner_category3]= COALESCE (p.[partner_category3],pc.[partner_category3])
				                ,[partner_category4]= COALESCE (p.[partner_category4],pc.[partner_category4])
                                ,[partner_category5]= COALESCE (p.[partner_category5],pc.[partner_category5])
                                ,[partner_category6]= COALESCE (p.[partner_category6],pc.[partner_category6])
				                ,[Partner_Price]= COALESCE (p.[Partner_Price],pc.[Partner_Price])
				                ,[sender]= COALESCE (p.[sender],pc.[sender])
				                ,[append_date]=COALESCE (p.[append_date],pc.[append_date])
                                ,[Material_Rebate]=COALESCE (p.[Material_Rebate],pc.[Material_Rebate])							
				                ,revised_material=
			                Case 
				                WHEN marketing_prod.dbo.fn_RegExMatchMatch(m.material,'-') > 0 THEN marketing_prod.dbo.fn_RegExReplace(m.material,'(-.+)','')

				                WHEN marketing_prod.dbo.fn_RegExMatchMatch(m.material,'US') > 0  and LEN(m.material) > 10 THEN marketing_prod.dbo.fn_RegExMatchReturn(m.material,'.+US')

				                ELSE m.material					  
			                END								
				                ,m.CatDash_level3			
			                INTO ##PM_cat_temp
			                -- SELECT * 
			                FROM [marketing_prod].[dbo].[prod_material] AS m 						  

			                LEFT JOIN
				                [marketing_work].[pm_na].[pm_categories_prd] AS p  ON p.Material =
				                CASE
						                WHEN marketing_prod.dbo.fn_RegExMatchMatch(m.material,'-') > 0 THEN marketing_prod.dbo.fn_RegExReplace(m.material,'(-.+)','')
						                WHEN marketing_prod.dbo.fn_RegExMatchMatch(m.material,'US') > 0 THEN marketing_prod.dbo.fn_RegExMatchReturn(m.material,'.+US')
				                ELSE m.material END AND p.SR_SoldTo=m.SR_Sold_To

			                LEFT JOIN
				                [marketing_work].[pm_na].[pm_categories_prd] AS pc on pc.Material=LEFT(m.material,4) AND pc.SR_SoldTo=m.SR_Sold_To
			 
			                WHERE 
					                m.SR_Sold_To = @Sr_sold_to	


		                UPDATE ##PM_cat_temp
		                SET [partner_category1]=	CASE WHEN marketing_prod.dbo.fn_RegExMatchMatch(material,'-SP')=1  THEN 'Spare Part'

										                WHEN CatDash_level3 = 'Servers' and left(revised_material,2) <> '30' THEN 'DCG'
										                WHEN len(revised_material) = 10 and left(revised_material,1) ='7' THEN 'DCG'
									                ELSE 'PCG'END  

		                UPDATE ##PM_cat_temp
		                SET [partner_category2]=CASE 
									                WHEN LEFT(revised_material,2)='10' and RIGHT(revised_material,2)='US' THEN 'Topseller ThinkCentre'
									                WHEN LEFT(revised_material,2)='10' THEN 'Corporate ThinkCentre'
									                WHEN LEFT(revised_material,2)='20' THEN 'Corporate ThinkPad'
									                WHEN LEFT(revised_material,2)='30' THEN 'Corporate ThinkStation'
									                else 'Other'
								                END

		                Where ##PM_cat_temp.[partner_category1] = 'PCG' and ##PM_cat_temp.[partner_category2] is null  

		                UPDATE ##PM_cat_temp
		                SET [partner_category3]=CASE WHEN p.material is not null THEN 'Premier Client Services' 
									                WHEN left(revised_material,2) ='30' THEN 'Workstation'
								                END
		                FROM ##PM_cat_temp

		                Left Join 
		                [marketing_work].[dbo].[jr_lenovo_premium] as p on p.material= ##PM_cat_temp.revised_material

		                Where   ##PM_cat_temp.[partner_category1] = 'PCG' and (##PM_cat_temp.[partner_category3] is null or p.material is not null)  
						 
		                UPDATE ##PM_cat_temp
		                SET [partner_category4]=CASE 
									                WHEN LEFT(revised_material,2) in ('10','20','30') THEN 'Commercial Proxy'
								                END

		                Where ##PM_cat_temp.[partner_category1] = 'PCG' and ##PM_cat_temp.[partner_category4] is null                 
              """
             ,'analyst':'yunior.rosellruiz@insight'}
          ,'10357882':
                {'cto_flag':True,
                  'cto_str_proc':"""
                       DROP TABLE IF EXISTS ##PM_cat_temp
			            DECLARE @Sr_sold_to nvarchar(10)='10357882';
                          SELECT        
								         [key]=m.[SR_Sold_To] +'|'+ m.material
                                        ,[sr_soldto]=m.SR_Sold_To
				                        ,m.material
				                        ,[material_type]= 'internal_part_cto_result'
				                        ,[partner_category1]= p.[partner_category1]
				                        ,[partner_category2]= p.[partner_category2]
				                        ,[partner_category3]= p.[partner_category3]
				                        ,[partner_category4]= p.[partner_category4]
                                        ,[partner_category5]= p.[partner_category5]
                                        ,[partner_category6]= p.[partner_category6]
				                        ,[Partner_Price]= p.[Partner_Price]
				                        ,[sender]= p.[sender]
				                        ,[append_date]=p.[append_date]
                                        ,[Material_Rebate]=p.[Material_Rebate]
	                     INTO ##PM_cat_temp
                 
				         FROM 
					        [marketing_work].[pm_na].[pm_categories_prd] AS p
	                

				          LEFT JOIN
						        [marketing_prod].[dbo].[prod_material] AS m ON 
						        p.material=SUBSTRING(m.mfr_part_number,9,2) 
						        and p.SR_SoldTo=m.SR_Sold_To										

				          WHERE 
						        p.Material_type='internal_part_cto'
						        AND p.SR_SoldTo=@Sr_sold_to
              """}
          ,'10986883':
                {'cto_flag':True,
                  'cto_str_proc':"""
			        DECLARE @Sr_sold_to nvarchar(10)='10986883';

                    SELECT 
							     [key]=m.[SR_Sold_To] +'|'+ m.material
                                ,[sr_soldto]=m.SR_Sold_To
				                ,m.material
				                ,[material_type]= 'internal_part_cto_result'
				                ,[partner_category1]= case 
                                                               when m.[material_group] in ('FB','FD','FG','FJ') then 'Barco | Collaboration'
                                                               when m.[material_description] like '%CSE%' then 'Barco | Collaboration'
							                                   when m.[material_description] like '%Clickshare%' then 'Barco | Collaboration'
							                                   when m.[material_description] like '%Wepresent%' then 'Barco | Collaboration'
							                                   when m.[material] like 'CSE%' then 'Barco | Collaboration'
                                                      else 'Barco | Display' end 
				                ,[partner_category2]= NULL
				                ,[partner_category3]= p.[partner_category3]
				                ,[partner_category4]= p.[partner_category4]
                                ,[partner_category5]= p.[partner_category5]
                                ,[partner_category6]= p.[partner_category6]
				                ,[Partner_Price]= p.[Partner_Price]
				                ,[sender]= p.[sender]
				                ,[append_date]=p.[append_date]
                                ,[Material_Rebate]=p.[Material_Rebate]

			         INTO ##PM_cat_temp
			          -- select * 
			         FROM 
			         [marketing_work].[pm_na].[pm_categories_prd] AS p
			 			
			         LEFT JOIN 
					        [marketing_prod].[dbo].[prod_material] AS m on p.Material=m.material and p.SR_SoldTo=m.SR_Sold_To
			         WHERE 
				        p.Material_type='internal_part_cto'
				        AND p.SR_SoldTo=@Sr_sold_to
              """}
          ,'10798467':
                {'cto_flag':True,
                  'cto_str_proc':"""
				  DECLARE @Sr_sold_to nvarchar(10)='10798467';

                  SELECT 
				                 [key]=m.[SR_Sold_To] +'|'+ m.material
                                ,[sr_soldto]=m.SR_Sold_To
				                ,m.material
				                ,[material_type]= 'internal_part'
				                ,[partner_category1]=CASE 
                                                  WHEN m.material like '%AFF%' THEN 'FLASH'
												  WHEN m.material like '%FAS%' THEN 'FAS'
												  WHEN m.material like '%AVA%' THEN 'ALTAVAULT'
												  WHEN m.material_description like '%CHOICE%' THEN 'FIRST CALL'
												  WHEN m.material_description like '%FIRE%' THEN 'SOLIDFIRE'
											      END 
				                ,[partner_category2]= NULL
				                ,[partner_category3]= NULL
				                ,[partner_category4]= NULL
                                ,[partner_category5]= NULL
                                ,[partner_category6]= NULL
				                ,[Partner_Price]= NULL
				                ,[sender]= NULL
				                ,[append_date]=NULL
                                ,[Material_Rebate]=NULL

			 INTO ##PM_cat_temp
			  -- select * 
			 FROM [marketing_prod].[dbo].[prod_material] AS m
			 WHERE m.SR_Sold_To=@Sr_sold_to
              """}
         ,'10278736':
                {'cto_flag':True,
                  'cto_str_proc':"""
                 DECLARE @Sr_sold_to nvarchar(10)='10278736';

                  SELECT 
				                 [key]=m.[SR_Sold_To] +'|'+ m.material
                                ,[sr_soldto]=m.SR_Sold_To
				                ,m.material
				                ,[material_type]= p.[material_type]
				                ,[partner_category1]= p.[partner_category1]
				                ,[partner_category2]= 
								CASE WHEN p.[partner_category2] ='Other' 
									THEN
										CASE
											 when left(m.[material],3) = 'CON' then 'Services'
											 when left(m.[material],2) in ('WS','C1') then 'Enterprise Networking'
											 when left(m.[material],5) = 'C3850' then 'Enterprise Networking'
											 when left(m.[material],3) in ('AIR','ASR','ISR') then 'Enterprise Networking'
											 when left(m.[material],3) in ('UMB','ESA','ASA') then 'Security'
											 when left(m.[material],9) = 'L-CSCO-SS' then 'Data Center'
											 else  p.[partner_category2]
										END
								END
				                ,[partner_category3]= p.[partner_category3]
				                ,[partner_category4]= p.[partner_category4]
                                ,[partner_category5]= p.[partner_category5]
                                ,[partner_category6]=p.[partner_category6]
				                ,[Partner_Price]= p.[Partner_Price]
				                ,[sender]= p.[sender]
				                ,[append_date]=p.[append_date]
                                ,[Material_Rebate]=p.[Material_Rebate]

			 INTO ##PM_cat_temp
			  -- select * 
			 FROM [marketing_prod].[dbo].[prod_material] AS m

			 INNER JOIN 
					[marketing_work].[pm_na].[pm_categories_prd] AS p on p.Material=m.material and p.SR_SoldTo=m.SR_Sold_To

			 WHERE 
					 m.SR_Sold_To = @Sr_sold_to
              """}
           }

