from django.contrib import admin
from .models import OrderStatus, Order, Applier, RefuseReasonsAfterTempStop, RefuseReasonsPreliminary, PPnumber, \
    Category, ResponsibleForOrderPreliminary, ResponsibleForOrderAfterTempStop, LotkiContent, OrderTypeCheck, \
    CategoriesByOrder, \
    LotkiRefuse, LotkiTempStop, LotkiEZ, NotificationTempStop, NotificationRefuse, TempStop, Refuse, \
    RefuseReasonsPreliminaryByOrders, \
    StatusChange, Counters, TempStopFiles, AfterTempStopDecision, RefuseReasonsAfterTempStopByOrders, RefuseFiles, \
    CountersLotki, CountersAdmin, LotkiStatusChange, EZdoc, EZpdf, CheckPreliminary, CheckPreliminaryResponsibleExpert, \
    CheckPreliminaryFileToCheck, CheckPreliminaryFileToCheckReturned, CheckPreliminaryFileToCheckFinal, \
    CheckAfterTempStop, CheckAfterTempStopFileToCheck, CheckAfterTempStopFileToCheckFinal, ReadyForOK, CommissionDate, \
    AppointedForOK, ProtocolOrders, Protocol

# Register your models here.

admin.site.register(OrderStatus)
admin.site.register(Order)
admin.site.register(Applier)
admin.site.register(RefuseReasonsPreliminary)
admin.site.register(RefuseReasonsAfterTempStop)
admin.site.register(PPnumber)
admin.site.register(Category)
admin.site.register(ResponsibleForOrderPreliminary)
admin.site.register(ResponsibleForOrderAfterTempStop)
admin.site.register(LotkiContent)
admin.site.register(OrderTypeCheck)
admin.site.register(CategoriesByOrder)
admin.site.register(LotkiTempStop)
admin.site.register(LotkiRefuse)
admin.site.register(LotkiEZ)
admin.site.register(NotificationRefuse)
admin.site.register(NotificationTempStop)
admin.site.register(Counters)
admin.site.register(TempStop)
admin.site.register(Refuse)
admin.site.register(RefuseReasonsPreliminaryByOrders)
admin.site.register(StatusChange)
admin.site.register(TempStopFiles)
admin.site.register(AfterTempStopDecision)
admin.site.register(RefuseReasonsAfterTempStopByOrders)
admin.site.register(RefuseFiles)
admin.site.register(CountersLotki)
admin.site.register(CountersAdmin)
admin.site.register(LotkiStatusChange)
admin.site.register(EZdoc)
admin.site.register(EZpdf)
admin.site.register(CheckPreliminary)
admin.site.register(CheckPreliminaryResponsibleExpert)
admin.site.register(CheckPreliminaryFileToCheck)
admin.site.register(CheckPreliminaryFileToCheckReturned)
admin.site.register(CheckPreliminaryFileToCheckFinal)
admin.site.register(CheckAfterTempStop)
admin.site.register(CheckAfterTempStopFileToCheck)
admin.site.register(CheckAfterTempStopFileToCheckFinal)
admin.site.register(ReadyForOK)
admin.site.register(CommissionDate)
admin.site.register(AppointedForOK)
admin.site.register(ProtocolOrders)
admin.site.register(Protocol)



