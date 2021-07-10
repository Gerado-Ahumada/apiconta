import json

from django.shortcuts import render
from rest_framework.response import Response,responses
from .models import LibroDiario
from .serializers import LibroDiarioSerializer,boletaSerializer,boletaDetalleSerializers,BalanceSerializer, facturaSerializer, facturaDetalleSerializers
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from .models import boleta, boletaDetalle
import requests
from django.db.models import Sum,Count,Case,When,IntegerField,F
# Create your views here.


class BoletaViewset(viewsets.ModelViewSet):
    queryset = boleta.objects.all()
    serializer_class = boletaSerializer

class BoletaDetalleViewset(viewsets.ModelViewSet):
    queryset = boletaDetalle.objects.all()
    serializer_class = boletaDetalleSerializers


@api_view(['GET'])
def LibroDiarioLista(request):
    librodiario = LibroDiario.objects.all()
    serializer = LibroDiarioSerializer(librodiario , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def BalanceDiario(request, pk):
    librodiario = LibroDiario.objects.all()
    librodiario = librodiario.filter(fecha=pk)
    serializer = LibroDiarioSerializer(librodiario , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def BalanceFechas(request, pk1,pk2):

    #query = 'select * from libroDiario'
    #with connection.cursor() as cursor:
        #cursor.execute(query)
        #serializer = LibroDiarioSerializer(cursor.fetchall(), many=True)
       # cursor.close()

    #librodiario = LibroDiario.objects.values('id_transaccion','nombre_transaccion').annotate(sum(Debe='debe').annotate(sum(Haber='haber')).filter(fecha__range= (pk1,pk2))    #Sum('haber')-Sum('debe'))
    librodiario = LibroDiario.objects.filter(fecha__range= (pk1,pk2)).values('id_transaccion','nombre_transaccion').annotate(Debe=Sum('debe')).annotate(Haber=Sum('haber')).annotate(SaldoDeudor = Sum('debe')-Sum('haber')).annotate(SaldoAcreedor = Sum('haber')-Sum('debe'))  #Case(When('debe' == 'haber',then=1),output_field=IntegerField())).annotate(SaldoAcreedor = Case(When('haber' == 'debe',then=1),output_field=IntegerField()))
    #librodiario = librodiario.objects.values()
    serializer = BalanceSerializer(librodiario , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def LibroDiarioDetalle(request, pk):
    librodiario = LibroDiario.objects.get(id=pk)
    serializer = LibroDiarioSerializer(librodiario, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def LibroDiarioCrear(request):
    serializer = LibroDiarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors)
    return Response(serializer.data)

@api_view(['DELETE'])
def LibroDiarioEliminar(request, pk):
    librodiario = LibroDiario.objects.get(id=pk)
    librodiario.delete()
    return Response('Eliminado')

@api_view(['POST'])
@parser_classes([JSONParser])
def boletaCrear(request):
    serializer = boletaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        url = "http://127.0.0.1:8000/LibroDiario/crear"
        headers = {'Content-type': 'application/json', }

        fecha_transaccion = serializer.data["fecha_venta"]

        pago_debe = serializer.data["total_v"]
        pago_haber = 0

	 # TRANSACCION CLIENTE DEBE
        hcliente_debe = serializer.data["total_v"]
        hcliente_haber = 0
        hcliente_id_transaccion = '005CLIENTE'
        hcliente_nombre_transaccion = 'CLIENTE'

        dataTransaccion = {'id_transaccion': hcliente_id_transaccion,
                           "nombre_transaccion": hcliente_nombre_transaccion,
                           "debe": hcliente_debe,
                           "haber": hcliente_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })


 	
        #TRANSACCION IVA DEBITO
        iva_debe = 0
        iva_haber = serializer.data["iva_total"]
        iva_id_transaccion = '003IVAD'
        iva_nombre_transaccion = 'IVA DEBITO'

        dataTransaccion = {'id_transaccion': iva_id_transaccion,
                           "nombre_transaccion": iva_nombre_transaccion,
                           "debe": iva_debe,
                           "haber": iva_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)

        # return render(request, '', {
        #     'response': response
        # })

        # # TRANSACCION VENTA
        venta_debe = 0
        venta_haber = serializer.data["neto_v"]
        venta_id_transaccion = '004VENTA'
        venta_nombre_transaccion = 'VENTAS'

        dataTransaccion = {'id_transaccion': venta_id_transaccion,
                           "nombre_transaccion": venta_nombre_transaccion,
                           "debe": venta_debe,
                           "haber": venta_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })

        #
	    # TRANSACCION CAJA-BANCO
        if serializer.data["metodo_pago"] == "1":
            pago_id_transaccion = '001CAJA'
            pago_nombre_transaccion = 'CAJA'

        elif serializer.data["metodo_pago"] == "2":
            pago_id_transaccion = '002BANCO'
            pago_nombre_transaccion = 'BANCO'
        else:
            pago_id_transaccion = '006CXC'
            pago_nombre_transaccion = 'CUENTAS POR COBRAR'

        dataTransaccion = {'id_transaccion': pago_id_transaccion,
                           "nombre_transaccion": pago_nombre_transaccion,
                           "debe": pago_debe,
                           "haber": pago_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })       

       # TRANSACCION CLIENTE HABER
        dcliente_debe = 0
        dcliente_haber = serializer.data["total_v"]
        dcliente_id_transaccion = '005CLIENTE'
        dcliente_nombre_transaccion = 'CLIENTE'

        dataTransaccion = {'id_transaccion': dcliente_id_transaccion,
                           "nombre_transaccion": dcliente_nombre_transaccion,
                           "debe": dcliente_debe,
                           "haber": dcliente_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })


        # TRANSACCION COSTO VENTA
        costo_debe = serializer.data["neto_c"]
        costo_haber = 0
        costo_id_transaccion = '007COSTOV'
        costo_nombre_transaccion = 'COSTO VENTA'

        dataTransaccion = {'id_transaccion': costo_id_transaccion,
                           "nombre_transaccion": costo_nombre_transaccion,
                           "debe": costo_debe,
                           "haber": costo_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })

        # TRANSACCION PRODUCTO
        producto_id_transaccion = '008PRODUCTO'
        producto_nombre_transaccion = 'PRODUCTO'
        producto_debe = 0
        producto_haber = serializer.data["neto_c"]


        dataTransaccion = {'id_transaccion': producto_id_transaccion,
                           "nombre_transaccion": producto_nombre_transaccion,
                           "debe": producto_debe,
                           "haber": producto_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)
        # return render(request, '', {
        #     'response': response
        # })

#[]
        # dataTransaccion ={'id_transaccion' : iva_id_transaccion,
        #                 "nombre_transaccion" : iva_nombre_transaccion,
        #                 "debe" : iva_debe,
        #                 "haber" : iva_haber,
        #                 "fecha" : fecha_transaccion
                         #},{'id_transaccion' : venta_id_transaccion,
                        # "nombre_transaccion" : venta_nombre_transaccion,
                        # "debe" : venta_debe,
                        # "haber" : venta_haber,
                        # "fecha" : fecha_transaccion
                        #     },{'id_transaccion' : dcliente_id_transaccion,
                        # "nombre_transaccion" : dcliente_nombre_transaccion,
                        # "debe" : dcliente_debe,
                        # "haber" : dcliente_haber,
                        # "fecha" : fecha_transaccion
                        #     },{'id_transaccion': hcliente_id_transaccion,
                        #  "nombre_transaccion": hcliente_nombre_transaccion,
                        #  "debe": hcliente_debe,
                        #  "haber": hcliente_haber,
                        #  "fecha": fecha_transaccion
                        #  },{'id_transaccion' : costo_id_transaccion,
                        # "nombre_transaccion" : costo_nombre_transaccion,
                        # "debe" : costo_debe,
                        # "haber" : costo_haber,
                        # "fecha" : fecha_transaccion
                        #     },{'id_transaccion' : producto_id_transaccion,
                        # "nombre_transaccion" : producto_nombre_transaccion,
                        # "debe" : producto_debe,
                        # "haber" : producto_haber,
                        # "fecha" : fecha_transaccion
                        #     }




    else:
        return Response(serializer.errors)
    return Response('Boleta Insertada')#Response(serializer.data)


@api_view(['POST'])
@parser_classes([JSONParser])
def facturaCrear(request):
    serializer = facturaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        url = "http://127.0.0.1:8000/LibroDiario/crear"
        headers = {'Content-type': 'application/json', }

        # TRANSACCION PRODUCTO OK
        # TRANSACCION IVA CREDITO OK
        # TRANSACCION PROVEEDOR HABER OK
        # TRANSACCION PROVEEDOR DEBE OK
        # TRANSACCION CAJA OK

        fecha_transaccion = serializer.data["fecha_venta"]

        # TRANSACCION PRODUCTO
        prd_producto_id_transaccion = '008PRODUCTO'
        prd_producto_nombre_transaccion = 'PRODUCTO'
        prd_producto_debe = serializer.data["neto_v"]
        prd_producto_haber = 0


        dataTransaccion = {'id_transaccion': prd_producto_id_transaccion,
                           "nombre_transaccion": prd_producto_nombre_transaccion,
                           "debe": prd_producto_debe,
                           "haber": prd_producto_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)

        # TRANSACCION IVA CREDITO
        ivac_id_transaccion = '009IVAC'
        ivac_nombre_transaccion = 'IVA CREDITO'
        ivac_debe = serializer.data["iva_total"]
        ivac_haber = 0

        dataTransaccion = {'id_transaccion': ivac_id_transaccion,
                           "nombre_transaccion": ivac_nombre_transaccion,
                           "debe": ivac_debe,
                           "haber": ivac_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)

        # TRANSACCION PROVEEDOR HABER
        prvH_id_transaccion = '010PRV'
        prvH_nombre_transaccion = 'PROVEEDOR'
        prvH_debe = 0
        prvH_haber = serializer.data["total_v"]

        dataTransaccion = {'id_transaccion': prvH_id_transaccion,
                           "nombre_transaccion": prvH_nombre_transaccion,
                           "debe": prvH_debe,
                           "haber": prvH_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)

        # TRANSACCION PROVEEDOR DEBE
        prvD_id_transaccion = '010PRV'
        prvD_nombre_transaccion = 'PROVEEDOR'
        prvD_debe = serializer.data["total_v"]
        prvD_haber = 0

        dataTransaccion = {'id_transaccion': prvD_id_transaccion,
                           "nombre_transaccion": prvD_nombre_transaccion,
                           "debe": prvD_debe,
                           "haber": prvD_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)

        # TRANSACCION CAJA-BANCO-CXP

        pago_debe = 0
        pago_haber = serializer.data["total_v"]

        if serializer.data["metodo_pago"] == "1":
            pago_id_transaccion = '001CAJA'
            pago_nombre_transaccion = 'CAJA'

        elif serializer.data["metodo_pago"] == "2":
            pago_id_transaccion = '002BANCO'
            pago_nombre_transaccion = 'BANCO'
        else:
            pago_id_transaccion = '011CXP'
            pago_nombre_transaccion = 'CUENTAS POR PAGAR'

        dataTransaccion = {'id_transaccion': pago_id_transaccion,
                           "nombre_transaccion": pago_nombre_transaccion,
                           "debe": pago_debe,
                           "haber": pago_haber,
                           "fecha": fecha_transaccion
                           }
        response = requests.post(url, data=json.dumps(dataTransaccion), headers=headers)


    else:
        return Response(serializer.errors)
    return Response('Factura Insertada')  # Response(serializer.data)

