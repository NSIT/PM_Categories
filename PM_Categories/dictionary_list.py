
#10112918 -Apple
#10920229 -Microsoft Surface
#10367579 -Lenovo PCG|DCG

sr_tables={
           '10112918':
                {'cto_flag':True,
                  'cto_str_proc':"""

                  DECLARE @Sr_sold_to nvarchar(10)='10112918';

                  SELECT 
				   [key]=m.[SR_Sold_To] +'|'+m.material
				  ,p.[sr_soldto]
				  ,m.material
				  ,p.[material_type]
				  ,p.[Partner_Category 1]
				  ,p.[Partner_Category 2]
				  ,p.[Partner_Category 3]
				  ,p.[Partner_Category 4]
                  ,p.[Partner_Category 5]
                  ,p.[Partner_Category 6]
				  ,p.[Partner_Price]
				  ,p.[sender]
				  ,p.[append_date]
                  ,p.[Material_Rebate]

			  INTO ##PM_cat_temp
			  -- select * 
			  FROM [marketing_work].[pm_na].[pm_categories_prd] AS p

			  INNER JOIN
					[marketing_prod].[dbo].[prod_material] AS m ON LEFT(m.material,LEN(m.material))=p.material

			  WHERE 
					 p.sr_soldto = @Sr_sold_to
					 AND p.material_type = 'internal_material_cto'
                     AND m.SR_Sold_To = @Sr_sold_to
              """
             ,'analyst':'yunior.rosellruiz@insight'}
          ,'10920229':
                {'cto_flag':False

                 ,'analyst':'yunior.rosellruiz@insight'}

          ,'10367579':
                {'cto_flag':True,
                  'cto_str_proc':"""
                     DECLARE @Sr_sold_to nvarchar(10)='10367579';
		            SELECT 
				               [key]=m.[SR_Sold_To] +'|'+m.material
				              ,p.[sr_soldto]
				              ,m.material
				              ,p.[material_type]
				              ,p.[Partner_Category 1]
				              ,p.[Partner_Category 2]
				              ,p.[Partner_Category 3]
				              ,p.[Partner_Category 4]
                              ,p.[Partner_Category 5]
                              ,p.[Partner_Category 6]
				              ,p.[Partner_Price]
				              ,p.[sender]
				              ,p.[append_date]
                              ,p.[Material_Rebate]
				              ,revised_material=Case 
						            when marketing_prod.dbo.fn_RegExMatchMatch(m.mfr_part_number,'-')= 1  then LEFT([mfr_part_number],CHARINDEX('-',[mfr_part_number])-1)
						            when (marketing_prod.dbo.fn_RegExMatchMatch(m.mfr_part_number,'US')=1 and len([mfr_part_number]) > 10) then LEFT([mfr_part_number],CHARINDEX('US',[mfr_part_number])+1)
						            else [mfr_part_number] end 
				               ,CatDash_level3

			              INTO ##PM_cat_temp
			              -- SELECT * 
			              FROM [marketing_work].[pm_na].[pm_categories_prd] AS p

			              INNER JOIN
					            [marketing_prod].[dbo].[prod_material] AS m ON LEFT(m.material,LEN(p.material))=p.material

			              WHERE 
					             p.sr_soldto = @Sr_sold_to
					             AND p.material_type = 'internal_part_cto'
					             AND m.SR_Sold_To = @Sr_sold_to 

			            UPDATE ##PM_cat_temp
			            SET [Partner_Category 1]=	CASE WHEN marketing_prod.dbo.fn_RegExMatchMatch(material,'-SP')=1  THEN 'Spare Part'

										              WHEN CatDash_level3 = 'Servers' and left(revised_material,2) <> '30' THEN 'DCG'
										              WHEN len(revised_material) = 10 and left(revised_material,1) ='7' THEN 'DCG'
										            ELSE 'PCG'END  

			            UPDATE ##PM_cat_temp
			            SET [Partner_Category 2]=CASE WHEN p.material is not null THEN 'Premier Client Services' 
										            WHEN left(revised_material,2)='30' THEN 'Workstation'
										            WHEN left(revised_material,2)='20' THEN 'All'
										            WHEN left(revised_material,2)='10' THEN 'Non-Premium'	
									            END
			            FROM ##PM_cat_temp

			            Left Join 
			            [marketing_work].[dbo].[jr_lenovo_premium] as p on p.material= ##PM_cat_temp.revised_material

			            Where   ##PM_cat_temp.[Partner_Category 1] = 'PCG' and (##PM_cat_temp.[Partner_Category 2] is null or p.material is not null)

			            UPDATE ##PM_cat_temp
			            SET [Partner_Category 3]=CASE 
										            WHEN LEFT(revised_material,2) in ('10','20','30') THEN 'Commercial'
									            END

			            Where ##PM_cat_temp.[Partner_Category 1] = 'PCG' and ##PM_cat_temp.[Partner_Category 3] is null

			            --MPC Desc
			            UPDATE ##PM_cat_temp
			            SET [Partner_Category 4]=CASE 
										            WHEN LEFT(revised_material,2)='10' and RIGHT(revised_material,2)='US' THEN 'Topseller ThinkCentre'
										            WHEN LEFT(revised_material,2)='10' THEN 'Corporate ThinkCentre'
										            WHEN LEFT(revised_material,2)='20' THEN 'Corporate ThinkPad'
										            WHEN LEFT(revised_material,2)='30' THEN 'Corporate ThinkStation'
										            else 'Other'
									            END

			            Where ##PM_cat_temp.[Partner_Category 1] = 'PCG' and ##PM_cat_temp.[Partner_Category 4] is null                         
              """
             ,'analyst':'yunior.rosellruiz@insight'}
           }
