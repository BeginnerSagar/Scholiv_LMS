import openpyxl
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance, Class

class AttendanceReportView(APIView):
    """
    API endpoint to download Attendance Reports as Excel.
    URL: /api/reports/attendance/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # --- DEBUGGING: Check what the server actually sees ---
        print(f"DEBUG: User='{user.username}' | Role stored in DB='{user.role}'")
        # ----------------------------------------------------

        # 1. Security Check (Robust & Case-Insensitive)
        # Convert to string, strip spaces, and make lowercase
        user_role = str(user.role).lower().strip() if user.role else ""
        
        allowed_roles = ['teacher', 'school_admin', 'super_admin']

        if user_role not in allowed_roles and not user.is_superuser:
            return Response({
                'error': f'Access Denied. Your role is "{user.role}", but only Teachers and Admins can download reports.'
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Get Query Parameters
        class_id = request.query_params.get('class_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not class_id:
            return Response({'error': 'class_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Fetch Data
        try:
            target_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({'error': 'Class not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Filter attendance records
        queryset = Attendance.objects.filter(student__assigned_class=target_class).select_related('student', 'lecture')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Order by date (newest first), then student name
        queryset = queryset.order_by('-date', 'student__first_name')

        # 4. Create Excel Workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Attendance - {target_class.name}"

        # --- Header Row ---
        headers = ["Date", "Student Name", "Student Email", "Lecture Title", "Status"]
        ws.append(headers)

        # Style the header (Bold + Center)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # --- Data Rows ---
        for record in queryset:
            status_text = "Present" if record.present else "Absent"
            
            row = [
                record.date,
                f"{record.student.first_name} {record.student.last_name}".strip(),
                record.student.email,
                record.lecture.title if record.lecture else "N/A",
                status_text
            ]
            ws.append(row)

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        # 5. Return File Response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="Attendance_Report_{target_class.name}.xlsx"'
        
        wb.save(response)
        return response
    

    