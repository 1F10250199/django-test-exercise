from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'],
                    due_at=make_aware(parse_datetime(request.POST['due_at'])))
        task.save()
    
    tasks = Task.objects.all()

    keyword = request.GET.get('keyword')
    if keyword:
        tasks = tasks.filter(title__icontains=keyword)

    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    context = {
        'tasks': tasks,
        'keyword': keyword,  
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not found')
    
    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html',context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def edit(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not found')

    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        due_at_value = request.POST.get('due_at', '')
        if due_at_value:
            task.due_at = make_aware(parse_datetime(due_at_value))
        else:
            task.due_at = None
        task.save()
        return redirect('detail', task_id=task.id)

    context = {
        'task': task,
    }
    return render(request, 'todo/edit.html', context)


def toggle_saved(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not found')
    task.saved = not task.saved
    task.save()
    # Redirect back to detail page
    return redirect('detail', task_id=task.id)


def saved_list(request):
    # Show only saved (favorited) tasks
    tasks = Task.objects.filter(saved=True).order_by('-posted_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'todo/saved.html', context)
