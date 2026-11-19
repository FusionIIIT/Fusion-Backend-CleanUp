import json

from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from PIL import Image
from applications.academic_information.models import Student
from applications.globals.forms import IssueForm, WebFeedbackForm
from applications.globals.models import (ExtraInfo, Feedback, HoldsDesignation,
                                         Issue, IssueImage, Faculty)
from applications.placement_cell.forms import (AddAchievement, AddCourse,
                                               AddEducation, AddExperience,
                                               AddPatent, AddProfile, AddConference,
                                               AddProject, AddPublication,
                                               AddSkill, AddReference, AddExtracurricular)
from applications.placement_cell.models import (Achievement, Course, Education, Conference,
                                                Experience, Has, Patent, Extracurricular,
                                                Project, Publication, Skill, Reference, PlacementStatus)
from applications.academic_procedures.models import Thesis


def contextstudentmanage(current,profile,request,user,editable):
  student = get_object_or_404(Student, Q(id=profile.id))
  reference_tab = 0

  if editable and request.method == 'POST':
      if 'studentapprovesubmit' in request.POST:
          status = PlacementStatus.objects.filter(pk=request.POST['studentapprovesubmit']).update(invitation='ACCEPTED', timestamp=timezone.now())
      if 'studentdeclinesubmit' in request.POST:
          status = PlacementStatus.objects.filter(Q(pk=request.POST['studentdeclinesubmit'])).update(invitation='REJECTED', timestamp=timezone.now())
      if 'educationsubmit' in request.POST:
          form = AddEducation(request.POST)
          if form.is_valid():
              institute = form.cleaned_data['institute']
              degree = form.cleaned_data['degree']
              grade = form.cleaned_data['grade']
              stream = form.cleaned_data['stream']
              sdate = form.cleaned_data['sdate']
              edate = form.cleaned_data['edate']
              education_obj = Education.objects.create(unique_id=student, degree=degree,
                                                       grade=grade, institute=institute,
                                                       stream=stream, sdate=sdate, edate=edate)
              education_obj.save()
      if 'profilesubmit' in request.POST:
          about_me = request.POST.get('about')
          age = request.POST.get('age')
          address = request.POST.get('address')
          contact = request.POST.get('contact')
          extrainfo_obj = ExtraInfo.objects.get(user=user)
          extrainfo_obj.about_me = about_me
          extrainfo_obj.date_of_birth = age
          extrainfo_obj.address = address
          extrainfo_obj.phone_no = contact
          extrainfo_obj.save()
          profile = get_object_or_404(ExtraInfo, Q(user=user))
      if 'picsubmit' in request.POST:
          form = AddProfile(request.POST, request.FILES)
          extrainfo_obj = ExtraInfo.objects.get(user=user)
          extrainfo_obj.profile_picture = form.cleaned_data["pic"]
          extrainfo_obj.save()
      if 'skillsubmit' in request.POST:
          form = AddSkill(request.POST)
          print('skill coming----------------\n\n')
          if form.is_valid():
              skill = form.cleaned_data['skill']
              skill_rating = form.cleaned_data['skill_rating']
              try:
                  skill_id = Skill.objects.get(skill=skill)
                  skill_id = None
              except Exception as e:
                  print(e)
                  skill_id = Skill.objects.create(skill=skill)
                  skill_id.save()

              if skill_id is not None:
                has_obj = Has.objects.create(unique_id=student,
                                           skill_id=skill_id,
                                           skill_rating = skill_rating)
                has_obj.save()
      if 'achievementsubmit' in request.POST:
          form = AddAchievement(request.POST)
          if form.is_valid():
              achievement = form.cleaned_data['achievement']
              achievement_type = form.cleaned_data['achievement_type']
              description = form.cleaned_data['description']
              issuer = form.cleaned_data['issuer']
              date_earned = form.cleaned_data['date_earned']
              achievement_obj = Achievement.objects.create(unique_id=student,
                                                           achievement=achievement,
                                                           achievement_type=achievement_type,
                                                           description=description,
                                                           issuer=issuer,
                                                           date_earned=date_earned)
      if 'extracurricularsubmit' in request.POST:
          form = AddExtracurricular(request.POST)
          if form.is_valid():
              event_name = form.cleaned_data['event_name']
              event_type = form.cleaned_data['event_type']
              description = form.cleaned_data['description']
              name_of_position = form.cleaned_data['name_of_position']
              date_earned = form.cleaned_data['date_earned']
              extracurricular_obj = Extracurricular.objects.create(unique_id=student,
                                                           event_name=event_name,
                                                           event_type=event_type,
                                                           description=description,
                                                           name_of_position=name_of_position,
                                                           date_earned=date_earned)
              extracurricular_obj.save()
      if 'publicationsubmit' in request.POST:
          form = AddPublication(request.POST)
          if form.is_valid():
              publication_title = form.cleaned_data['publication_title']
              description = form.cleaned_data['description']
              publisher = form.cleaned_data['publisher']
              publication_date = form.cleaned_data['publication_date']
              publication_obj = Publication.objects.create(unique_id=student,
                                                           publication_title=
                                                           publication_title,
                                                           publisher=publisher,
                                                           description=description,
                                                           publication_date=publication_date)
              publication_obj.save()
      if 'patentsubmit' in request.POST:
          form = AddPatent(request.POST)
          if form.is_valid():
              patent_name = form.cleaned_data['patent_name']
              description = form.cleaned_data['description']
              patent_office = form.cleaned_data['patent_office']
              patent_date = form.cleaned_data['patent_date']
              patent_obj = Patent.objects.create(unique_id=student, patent_name=patent_name,
                                                 patent_office=patent_office,
                                                 description=description,
                                                 patent_date=patent_date)
              patent_obj.save()
      if 'coursesubmit' in request.POST:
          form = AddCourse(request.POST)
          if form.is_valid():
              course_name = form.cleaned_data['course_name']
              description = form.cleaned_data['description']
              license_no = form.cleaned_data['license_no']
              sdate = form.cleaned_data['sdate']
              edate = form.cleaned_data['edate']
              course_obj = Course.objects.create(unique_id=student, course_name=course_name,
                                                 license_no=license_no,
                                                 description=description,
                                                 sdate=sdate, edate=edate)
              course_obj.save()

      if 'conferencesubmit' in request.POST:
          form = AddConference(request.POST)
          if form.is_valid():
              conference_name = form.cleaned_data['conference_name']
              description = form.cleaned_data['description']
              sdate = form.cleaned_data['sdate']
              edate = form.cleaned_data['edate']
              conference_obj = Conference.objects.create(unique_id=student, conference_name=conference_name,
                                                 description=description,
                                                 sdate=sdate, edate=edate)
              conference_obj.save()
      if 'projectsubmit' in request.POST:
          form = AddProject(request.POST)
          if form.is_valid():
              project_name = form.cleaned_data['project_name']
              project_status = form.cleaned_data['project_status']
              summary = form.cleaned_data['summary']
              project_link = form.cleaned_data['project_link']
              sdate = form.cleaned_data['sdate']
              edate = form.cleaned_data['edate']
              project_obj = Project.objects.create(unique_id=student, summary=summary,
                                                   project_name=project_name,
                                                   project_status=project_status,
                                                   project_link=project_link,
                                                   sdate=sdate, edate=edate)
              project_obj.save()
      if 'experiencesubmit' in request.POST:
          form = AddExperience(request.POST)
          if form.is_valid():
              title = form.cleaned_data['title']
              status = form.cleaned_data['status']
              company = form.cleaned_data['company']
              location = form.cleaned_data['location']
              description = form.cleaned_data['description']
              sdate = form.cleaned_data['sdate']
              edate = form.cleaned_data['edate']
              experience_obj = Experience.objects.create(unique_id=student, title=title,
                                                         company=company, location=location,
                                                         status=status,
                                                         description=description,
                                                         sdate=sdate, edate=edate)
              experience_obj.save()

      if 'addreference' in request.POST:
          form = AddReference(request.POST)
          reference_tab = 1
          print(form.errors)
          if form.is_valid():
              reference_name = form.cleaned_data['reference_name']
              post = form.cleaned_data['post']
              email = form.cleaned_data['email']
              mobile_number = form.cleaned_data['mobile_number']

              Reference.objects.create(
                  unique_id=student,
                  reference_name=reference_name,
                  post=post,
                  email=email,
                  mobile_number=mobile_number)
              messages.success(request, "Successfully added your reference!")

      if 'deleteskill' in request.POST:
          hid = request.POST['deleteskill']
          hs = Has.objects.get(Q(pk=hid))
          hs.delete()
      if 'deleteedu' in request.POST:
          hid = request.POST['deleteedu']
          hs = Education.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletecourse' in request.POST:
          hid = request.POST['deletecourse']
          hs = Course.objects.get(Q(pk=hid))
          hs.delete()
      if 'deleteexp' in request.POST:
          hid = request.POST['deleteexp']
          hs = Experience.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletepro' in request.POST:
          hid = request.POST['deletepro']
          hs = Project.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletereference' in request.POST:
          hid = request.POST['deletereference']
          hs = Reference.objects.get(Q(pk=hid))
          hs.delete()
      if 'deleteach' in request.POST:
          hid = request.POST['deleteach']
          hs = Achievement.objects.get(Q(pk=hid))
          hs.delete()
      if 'deleteconference' in request.POST:
          hid = request.POST['deleteconference']
          hs = Conference.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletextra' in request.POST:
          hid = request.POST['deletextra']
          hs = Extracurricular.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletepub' in request.POST:
          hid = request.POST['deletepub']
          hs = Publication.objects.get(Q(pk=hid))
          hs.delete()
      if 'deletepat' in request.POST:
          hid = request.POST['deletepat']
          hs = Patent.objects.get(Q(pk=hid))
          hs.delete()
  form = AddEducation(initial={})
  form1 = AddProfile(initial={})
  form10 = AddSkill(initial={})
  form11 = AddCourse(initial={})
  form12 = AddAchievement(initial={})
  form5 = AddPublication(initial={})
  form6 = AddProject(initial={})
  form7 = AddPatent(initial={})
  form8 = AddExperience(initial={})
  form14 = AddProfile()
  form15 = AddReference()
  form88 = AddExtracurricular()
  form62 = AddConference()
  skills = Has.objects.filter(Q(unique_id=student))
  education = Education.objects.filter(Q(unique_id=student))
  course = Course.objects.filter(Q(unique_id=student))
  conferences = Conference.objects.filter(Q(unique_id=student))
  experience = Experience.objects.filter(Q(unique_id=student))
  project = Project.objects.filter(Q(unique_id=student))
  achievement = Achievement.objects.filter(Q(unique_id=student))
  reference = Reference.objects.filter(Q(unique_id=student))
  extracurriculars = Extracurricular.objects.filter(Q(unique_id=student))
  publication = Publication.objects.filter(Q(unique_id=student))
  patent = Patent.objects.filter(Q(unique_id=student))
  context = {
    'user': user, 'profile': profile, 'skills': skills, 'extracurriculars': extracurriculars,
    'educations': education, 'courses': course, 'experiences': experience, 'conferences': conferences,
    'projects': project, 'achievements': achievement, 'publications': publication,
    'patent': patent, 'form': form, 'form1': form1, 'form14': form14, 'form62': form62,
    'form5': form5, 'form6': form6, 'form7': form7, 'form8': form8, 'form88': form88,
    'form10':form10, 'form11':form11, 'form12':form12, 'current':current,  'form15': form15,
    'editable': editable,  'reference_tab': reference_tab, 'references': reference
  }
  return context
