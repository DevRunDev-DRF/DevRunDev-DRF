from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _


class DevRunDevAdminSite(AdminSite):
    """커스텀 관리자 사이트"""

    # 사이트 타이틀 설정
    site_title = _("DevRunDev 관리자")
    site_header = _("DevRunDev 관리자 페이지")
    index_title = _("DevRunDev 관리자 대시보드")

    def each_context(self, request):
        context = super().each_context(request)
        context["available_apps"] = self.get_app_list(request)
        return context


# 기본 AdminSite 대신 커스텀 AdminSite 사용
admin.site = DevRunDevAdminSite()

# Django 기본 앱 등록
admin.site.register(Site)


# 관리자 페이지 인덱스 커스터마이징
admin.site.index_template = "admin/custom_index.html"
