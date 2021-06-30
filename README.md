# GGFastChemConverter
A script to convert GGchem's output to FastChem's formatting in order to function with ktable and subsequently HELIOS.

A short discription of how this code works is that it takes all columns from the GGchem output that are relevant to ktable (the ones about temperature, pressure, hydrogen abundance, electron abundance, gas phase abundances and condensate abundances) and converts them to the way FastChem would. The differences between FastChem output and GGchem output are:
  1. For the abundances of the different (gas) species, FastChem uses mixing ratios relative to H, while GGchem uses abundances.
  2. GGchem outputs almost all columns in logarithmic10 units, while FastChem does not.
  3. Column labels (i.e. FastChem labels the column with pressure values as 'Pbar', while GGchem labels it as 'pgas').
  4. GGchem does not include a column with the mean molecular weights by default. In this readme, you'll learn how to incorporate this. This has to be done for ktable to run with GGchem.
  5. Column order (not a problem since ktable functions regardless of column order)

The code therefore converts the first three points from GGchem's style to FastChem's style, independently of your chosen input parameters.

Here follows a step-by-step of how to add mean molecular weight values to GGchem output. Please use the suggested designation for the column label, otherwise this script will not work.

  1. Firstly, after you have compiled GGchem, you can find and edit the FORTRAN file demo_structure.f in the src16 directory. 
  2. In this file, find the lines of code where the output file (Static_Conc.dat) is written out. In my version of GGchem, this is in line 345. After the line 

     &               'dust/gas','dustVol/H','Jstar(W)','Nstar(W)'
     
     add a comma at the end, and a new line that says
     
     &               'mu/amu'
  3. Next, find the line in which the value of this column is written, in my version on line 470. Add another comma to the final line you find there in order to add another line, namely

     &       LOG10(mu/amu)
     
     This will output mean molecular weight values in logarithmic10 values.
  4. Recompile the code and run ggchem with your input. You can now check if Static_Conc.dat actually has your mu/amu column, which should be the final column there.

You can now use HELIOSGGchem.py to change this output to FastChem formatting by inputting the name of your output file (i.e. Static_Conc.dat) and your desired name for the output file (i.e. chemlow.dat or chemhigh.dat).
