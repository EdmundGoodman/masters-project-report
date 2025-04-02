# Set the program used to generate the PDF
# 1=pdflatex, 4=lualatex, 5=xelatex
$pdf_mode = 1;

# Set the TeX flags to set
set_tex_cmds("-interaction=nonstopmode -file-line-error -shell-escape -synctex=1 %O %S");
