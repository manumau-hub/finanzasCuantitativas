from tkinter import *

from opcion_europea_bin import opcion_europea_bin
from opcion_europea_fd import opcion_europea_fd
from opcion_europea_mc import opcion_europea_mc
from opcion_europea_bs import opcion_europea_bs

from opcion_americana_fd import opcion_americana_fd
from opcion_americana_bin import opcion_americana_bin

class MyWindow:
    def __init__(self, win):

        self.lbl_ejercicio = Label(win, text='Tipo de Ejercicio: ')
        self.lbl_ejercicio.place(x=10, y=40)

        self.ejercicio_lbl = IntVar()
        self.ejercicio_lbl.set(1)
        r1 = Radiobutton(window, text="Europea", variable=self.ejercicio_lbl, value=1)
        r2 = Radiobutton(window, text="Americana", variable=self.ejercicio_lbl, value=2)
        r1.place(x=150, y=40)
        r2.place(x=250, y=40)

        self.lbl_tipo = Label(win, text='Tipo de contrato: ')
        self.lbl_tipo.place(x=10, y=80)

        self.tipo_lbl = IntVar()
        self.tipo_lbl.set(1)
        r1 = Radiobutton(window, text="CALL", variable=self.tipo_lbl, value=1)
        r2 = Radiobutton(window, text="PUT", variable=self.tipo_lbl, value=2)
        r1.place(x=150, y=80)
        r2.place(x=250, y=80)

        self.lbl1 = Label(win, text='Precio Spot -                                            S :')
        self.lbl2 = Label(win, text='Precio de ejercicio -                                K : ')
        self.lbl3 = Label(win, text='Tiempo de expiracion en dias -           T : ')
        self.lbl4 = Label(win, text='Tasa libre de riesgo anualizada -           r : ')
        self.lbl5 = Label(win, text='Volatilidad implicita anualizada - sigma: ')
        self.lbl6 = Label(win, text='Tasa de dividendos anualizada -       div: ')

        self.lbloutput = Label(win, text='Precio de la opcion:')
        self.lblvar_mc = Label(win, text='Varianza de MC:')


        self.S_lbl = Entry()
        self.K_lbl = Entry()
        self.T_lbl = Entry()
        self.r_lbl = Entry()
        self.sigma_lbl = Entry()
        self.div_lbl = Entry()

        self.output = Entry()
        #self.var_mc = Entry()

        self.lbl1.place(x=10, y=150)
        self.S_lbl.place(x=225, y=150)

        self.lbl2.place(x=10, y=175)
        self.K_lbl.place(x=225, y=175)

        self.lbl3.place(x=10, y=200)
        self.T_lbl.place(x=225, y=200)

        self.lbl4.place(x=10, y=225)
        self.r_lbl.place(x=225, y=225)

        self.lbl5.place(x=10, y=250)
        self.sigma_lbl.place(x=225, y=250)

        self.lbl6.place(x=10, y=275)
        self.div_lbl.place(x=225, y=275)

        self.modelo_lbl = IntVar()
        self.modelo_lbl.set(1)
        r1 = Radiobutton(window, text="Black Scholes", variable=self.modelo_lbl, value=1)
        r2 = Radiobutton(window, text="Binomial", variable=self.modelo_lbl, value=2)
        r3 = Radiobutton(window, text="Montecarlo", variable=self.modelo_lbl, value=3)
        r4 = Radiobutton(window, text="Diferencias Finitas", variable=self.modelo_lbl, value=4)

        r1.place(x=50, y=320)
        r2.place(x=150, y=320)
        r3.place(x=250, y=320)
        r4.place(x=350, y=320)

        self.b1 = Button(win, text='Calcular precio opcion', command=self.calculate)
        self.b1.place(x=175, y=390)

        self.lbloutput.place(x=115, y=435)

        self.output.place(x=225, y=435)

        #self.lblvar_mc.place(x=10, y=475)
        #self.var_mc.place(x=225, y=475)

        self.lbltrademark = Label(win, text='Manu Maurette - 2022')

        self.lbltrademark.place(x=380, y=583)




        self.S_lbl.insert(END, 100.0)
        self.K_lbl.insert(END, 100.0)
        self.T_lbl.insert(END, 90)
        self.r_lbl.insert(END, 0.05)
        self.sigma_lbl.insert(END, 0.25)
        self.div_lbl.insert(END, 0.0)

        

        self.lblBIN = Label(win, text='Pasos Bin:')
        self.lblMC = Label(win, text='Caminos MC:')
        self.lblFD = Label(win, text='Pasos DF:')

        self.BIN_lbl = Entry()
        self.MC_lbl = Entry()
        self.FD_lbl = Entry()
    

        self.BIN_lbl.place(x=60, y=360)
        self.lblBIN.place(x=100, y=340)

        self.MC_lbl.place(x=200, y=360)
        self.lblMC.place(x=220, y=340)

        self.FD_lbl.place(x=340, y=360)
        self.lblFD.place(x=370, y=340)

        self.BIN_lbl.insert(END, 1000)
        self.MC_lbl.insert(END, 1000)
        self.FD_lbl.insert(END, 100)




    def calculate(self):
        #borro lo que habia
        self.output.delete(0, 'end')
        #inicializo
        if self.tipo_lbl.get() == 1:
            tipo = "C"
        elif self.tipo_lbl.get() == 2:
            tipo = "P"

        #Inputs
        S=float(self.S_lbl.get())
        K=float(self.K_lbl.get())
        T = float(self.T_lbl.get())/365.0
        r = float(self.r_lbl.get())
        sigma = float(self.sigma_lbl.get())
        div = float(self.div_lbl.get())

        bin_pasos = int(self.BIN_lbl.get())
        mc_caminos = int(self.MC_lbl.get())
        fd_pasos = int(self.FD_lbl.get())

        if self.modelo_lbl.get() == 1:
            if self.ejercicio_lbl.get() ==1:
                precio = opcion_europea_bs(tipo, S, K, T, r, sigma, div)
            elif self.ejercicio_lbl.get() ==2:
                precio = 'NA'
            else:
                precio = 'Error'

        elif self.modelo_lbl.get() == 2 :

            if self.ejercicio_lbl.get() == 1:
                precio = opcion_europea_bin(tipo, S, K, T, r, sigma, div, bin_pasos)
            elif self.ejercicio_lbl.get() == 2:
                precio = opcion_americana_bin(tipo, S, K, T, r, sigma, div, bin_pasos)
            else:
                precio = 'Error'
        elif self.modelo_lbl.get() == 3 :
            if self.ejercicio_lbl.get() == 1:
                precio = opcion_europea_mc(tipo, S, K, T, r, sigma, div, mc_caminos)

         #       try:
         #           self.var_mc.insert(END, round(var, 4))
         #       except:
         #           self.var_mc.insert(END, var)

            elif self.ejercicio_lbl.get() ==2:
                precio = 'NA'
            else:
                precio ='Error'
        elif self.modelo_lbl.get() == 4 :
                  
            if self.ejercicio_lbl.get() == 1:
                precio = opcion_europea_fd(tipo, S, K, T, r, sigma, div, fd_pasos)
            elif self.ejercicio_lbl.get() == 2:
                precio = opcion_americana_fd(tipo, S, K, T, r, sigma, div, fd_pasos)
            else:
                precio = 'Error'
        else:
            precio = 'Error'
        try:
            self.output.insert(END, round(precio,4))
        except:
            self.output.insert(END, precio)

window=Tk()
mywin=MyWindow(window)
window.title('Calculadora Opciones - UCEMA QUANt 2022')
window.geometry("500x600+15+15")
window.mainloop()