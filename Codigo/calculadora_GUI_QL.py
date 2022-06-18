from telnetlib import BINARY
from tkinter import *

import QuantLib as ql

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

        self.lbloutput_npv = Label(win, text='Precio de la opcion (QL):')
        self.lbloutput_delta = Label(win, text='Delta de la opcion (QL):')
        self.lbloutput_gamma = Label(win, text='Gamma de la opcion (QL):')
        self.lbloutput_vega = Label(win, text='Vega de la opcion (QL):')
        self.lbloutput_theta = Label(win, text='Theta de la opcion (QL):')
        self.lbloutput_rho = Label(win, text='Rho de la opcion (QL):')
        
        #self.lblvar_mc = Label(win, text='Varianza de MC:')

        #intputs
        self.S_lbl = Entry()
        self.K_lbl = Entry()
        self.T_lbl = Entry()
        self.r_lbl = Entry()
        self.sigma_lbl = Entry()
        self.div_lbl = Entry()

        #outputs
        self.output_npv = Entry()
        self.output_delta = Entry()
        self.output_gamma = Entry()
        self.output_vega = Entry()
        self.output_theta = Entry()
        self.output_rho = Entry()

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

        self.lbl_modelo = Label(win, text='Modelo: ')
        self.lbl_modelo.place(x=10, y=300)

        self.modelo_lbl = IntVar()
        self.modelo_lbl.set(1)
        r1 = Radiobutton(window, text="Analitico (BS/BAW)", variable=self.modelo_lbl, value=1)
        r2 = Radiobutton(window, text="Binomial", variable=self.modelo_lbl, value=2)
        r3 = Radiobutton(window, text="Montecarlo", variable=self.modelo_lbl, value=3)
        r4 = Radiobutton(window, text="Diferencias Finitas", variable=self.modelo_lbl, value=4)

        r1.place(x=10, y=320)
        r2.place(x=170, y=320)
        r3.place(x=300, y=320)
        r4.place(x=430, y=320)

        self.b1 = Button(win, text='Calcular precio opcion', command=self.calculate)
        self.b1.place(x=175, y=390)

        self.lbloutput_npv.place(x=90, y=435)
        self.output_npv.place(x=235, y=435)

        self.lbloutput_delta.place(x=90, y=460)
        self.output_delta.place(x=235, y=460)
        
        self.lbloutput_gamma.place(x=90, y=485)
        self.output_gamma.place(x=235, y=485)
        
        self.lbloutput_vega.place(x=90, y=510)
        self.output_vega.place(x=235, y=510)
        
        self.lbloutput_theta.place(x=90, y=535)
        self.output_theta.place(x=235, y=535)
        
        self.lbloutput_rho.place(x=90, y=560)
        self.output_rho.place(x=235, y=560)





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

        

        self.lblBIN = Label(win, text='Pasos Bin (<25K):')
        self.lblMC = Label(win, text='Caminos MC (<2.5M):')
        self.lblFD = Label(win, text='Pasos DF (<2.5K):')

        self.BIN_lbl = Entry()
        self.MC_lbl = Entry()
        self.FD_lbl = Entry()
    

        self.BIN_lbl.place(x=140, y=360)
        self.lblBIN.place(x=140, y=340)

        self.MC_lbl.place(x=280, y=360)
        self.lblMC.place(x=280, y=340)

        self.FD_lbl.place(x=430, y=360)
        self.lblFD.place(x=430, y=340)

        self.BIN_lbl.insert(END, 1000)
        self.MC_lbl.insert(END, 1000)
        self.FD_lbl.insert(END, 100)




    def calculate(self):
        #borro lo que habia
        self.output_npv.delete(0, 'end')
        self.output_delta.delete(0, 'end')
        self.output_gamma.delete(0, 'end')
        self.output_vega.delete(0, 'end')
        self.output_theta.delete(0, 'end')
        self.output_rho.delete(0, 'end')


        #inicializo

        #Inputs
        precio_activo = float(self.S_lbl.get())
        precio_ejercicio=float(self.K_lbl.get())
        tasa_interes = float(self.r_lbl.get())
        volatilidad = float(self.sigma_lbl.get())
        tasa_dividendos = float(self.div_lbl.get())

        #Inputs de modelos
        bin_pasos = int(self.BIN_lbl.get())
        mc_caminos = int(self.MC_lbl.get())
        fd_pasos = int(self.FD_lbl.get())  

        #Imput del tiempo a madurez
        T = int(self.T_lbl.get())
        fecha_valuacion = ql.Date(6, 8, 2022)

        ql.Settings.instance().evaluationDate = fecha_valuacion
        
        calendario = ql.UnitedStates()
        day_count = ql.Actual365Fixed()
        fecha_expiracion = fecha_valuacion + T
        
        if self.tipo_lbl.get() == 1:
            tipo_opcion = ql.Option.Call #Tipo de opcion (CALL o PUT)
        elif self.tipo_lbl.get() == 2:
            tipo_opcion = ql.Option.Put #Tipo de opcion (CALL o PUT)

        payoff = ql.PlainVanillaPayoff(tipo_opcion, precio_ejercicio)
        
        if self.ejercicio_lbl.get() == 1:
            ejercicio = ql.EuropeanExercise(fecha_expiracion)
            
        elif self.ejercicio_lbl.get() ==2:
            ejercicio = ql.AmericanExercise(fecha_valuacion, fecha_expiracion)

        opcion = ql.VanillaOption(payoff, ejercicio)    

        #Inputs para QL

        objeto_spot = ql.QuoteHandle(ql.SimpleQuote(precio_activo))
        objeto_tasa_interes = ql.YieldTermStructureHandle(ql.FlatForward(fecha_valuacion, 
                                                                tasa_interes, 
                                                                day_count))
        objeto_tasa_dividendos = ql.YieldTermStructureHandle(ql.FlatForward(fecha_valuacion, 
                                                      tasa_dividendos, 
                                                      day_count))
        objeto_volatilidad = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(fecha_valuacion, 
                                                                 calendario, 
                                                                 volatilidad, 
                                                             day_count))

        #Proceso BSM
        proceso_BSM = ql.BlackScholesMertonProcess(objeto_spot, 
                                           objeto_tasa_dividendos, 
                                           objeto_tasa_interes, 
                                           objeto_volatilidad)

        
        if self.modelo_lbl.get() == 1:
            if self.ejercicio_lbl.get() ==1:
                modelo_BS = ql.AnalyticEuropeanEngine(proceso_BSM)
                opcion.setPricingEngine(modelo_BS)
            elif self.ejercicio_lbl.get() ==2:
                modelo_BjS = ql.BaroneAdesiWhaleyApproximationEngine(proceso_BSM)
                opcion.setPricingEngine(modelo_BjS)
   


        elif self.modelo_lbl.get() == 2 :

            modelo_arbol = 'LR'
            cant_pasos_arbol = bin_pasos   

            modelo_Bin = ql.BinomialVanillaEngine(proceso_BSM, 
                                      modelo_arbol, 
                                      cant_pasos_arbol)

            opcion.setPricingEngine(modelo_Bin)

        elif self.modelo_lbl.get() == 3 :
            generador_numeros_aleatorios = "PseudoRandom" 
            pasos_tiempo=20
            caminos = mc_caminos
            if self.ejercicio_lbl.get() == 1:

                modelo_MC = ql.MCEuropeanEngine(proceso_BSM, 
                                generador_numeros_aleatorios, 
                                timeSteps = pasos_tiempo,
                                requiredSamples = caminos)

            elif self.ejercicio_lbl.get() ==2:
                
                modelo_MC = ql.MCAmericanEngine(proceso_BSM, 
                                generador_numeros_aleatorios, 
                                timeSteps = pasos_tiempo,
                                requiredSamples = caminos)
            
            opcion.setPricingEngine(modelo_MC)


        elif self.modelo_lbl.get() == 4 :

            tGrid = fd_pasos
            xGrid = fd_pasos
            dampingSteps = 0
            esquema_df = ql.FdmSchemeDesc.MethodOfLines()
            modelo_DF = ql.FdBlackScholesVanillaEngine(proceso_BSM, 
                                           tGrid, 
                                           xGrid,
                                           dampingSteps,
                                           esquema_df)

            opcion.setPricingEngine(modelo_DF)
            #precio = opcion.NPV()



        
        try:
            precio = opcion.NPV()    
        except:
            precio = 'NA'

        try:
            delta = opcion.delta()    
        except:
            delta = 'NA'
        
        try:
            gamma = opcion.gamma()    
        except:
            gamma = 'NA'
        
        try:
            vega = opcion.vega()/100    
        except:
            vega = 'NA'
        
        try:
            theta = opcion.theta()/365    
        except:
            theta = 'NA'

        try:
            rho = opcion.rho()/100    
        except:
            rho = 'NA'

        #else:
            
        try:
            self.output_npv.insert(END, round(precio,4))
        except:
            self.output_npv.insert(END, precio)
        
        try:
            self.output_delta.insert(END, round(delta,4))
        except:
            self.output_delta.insert(END, delta)
        
        try:
            self.output_gamma.insert(END, round(gamma,4))
        except:
            self.output_gamma.insert(END, gamma)

        try:
            self.output_vega.insert(END, round(vega,4))
        except:
            self.output_vega.insert(END, vega)
        
        try:
            self.output_theta.insert(END, round(theta,4))
        except:
            self.output_theta.insert(END, theta)
        
        try:
            self.output_rho.insert(END, round(rho,4))
        except:
            self.output_rho.insert(END, rho)
        

        




window=Tk()
mywin=MyWindow(window)
window.title('Calculadora Opciones QL - Exactas 2022')
window.geometry("600x700+15+15")
window.mainloop()