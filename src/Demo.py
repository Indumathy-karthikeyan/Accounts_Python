from fpdf.fpdf import FPDF


class Demo:

    def preparing(self):

        print("Hai")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Welcome to Python!", ln=1, align="C")
        pdf.cell(200, 20, txt="Hai", ln=1, align="C")
        pdf.output("simple_demo.pdf")
        print("Success")
