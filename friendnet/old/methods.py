# #!/usr/bin/env python
# # coding: utf-8
# # created by hevlhayt@foxmail.com
# # Date: 2016/5/16
# # Time: 19:56
# #
# import datetime
# import json
# import random
# import re
# from collections import Counter
#
# import networkx as nx
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.db.models import Q, Count
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
#
# from LineMe.constants import GROUP_MAXSIZE, GROUP_CREATED_CREDITS_COST, SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE, \
#     TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE, SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE, \
#     TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE, CITIES_TABLE
# from Human.models import Privacy, Extra, GroupMember, Link, Group, Credits, MemberRequest
# from Human.utils import create_avatar, logger_join, validate_user, validate_email, validate_passwd, group_name_existed, \
#     get_session_id, create_session_id, login_user
# from LineMe.settings import logger
#
#
# # Todo: separate to different files
#
# def create_user(request, name, email, password, password2):
#
#     if not validate_user(name):
#         return -1
#     elif not validate_email(email):
#         return -2
#     elif not validate_passwd(password, password2):
#         return -3
#     else:
#
#         # Todo: add finally
#         try:
#
#             u = User.objects.create_user(name, email, password)
#             login_user(request, name, password)
#
#             # Todo: impl privacy module
#             pri = Privacy(user=u, link_me=True, see_my_global=True)
#             pri.save()
#             extra = Extra(user=u,
#                           sex=False,
#
#                           # Todo: django timezone?
#                           birth=datetime.date.today(),
#                           credits=30,
#                           privacy=pri)
#
#             extra.save()
#             create_avatar(request, u.id, name)
#         except Exception, e:
#             # print 'Create user failed: ', e
#             logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
#             return -4
#
#         logger.info(logger_join('Create', get_session_id(request)))
#         return 0
#
#
# ########################################################################
#
# def get_user_name(user):
#     last = user.last_name
#     first = user.first_name
#     if len(first) is 0 and len(last) is 0:
#         return user.username
#     else:
#         return first + ' ' + last
#
#
# def get_user_groups(user):
#     gms = GroupMember.objects.filter(user=user, is_joined=True)
#
#     groups = [gm.group for gm in gms]
#
#     return groups
#
#
# def get_user_msgs(user):
#     my_members = GroupMember.objects.filter(user=user)
#
#     msgs = []
#     for mm in my_members:
#         # msgs += Link.objects.filter(Q(source_member=mm, status=0) |
#         #                              Q(target_member=mm, status=0) |
#         #                              Q(source_member=mm, status=2) |
#         #                              Q(target_member=mm, status=1) |
#         #                              Q(source_member=mm, status=-2) |
#         #                              Q(source_member=mm, status=-1), ~Q(creator=user))
#
#         msgs += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
#                                     Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
#                                     ~Q(creator=user))
#
#     return msgs
#
#
# def get_user_msgs_count(user):
#     my_members = GroupMember.objects.filter(user=user)
#
#     count = 0
#     for mm in my_members:
#         count += Link.objects.filter((Q(source_member=mm) & (Q(status=0) | Q(status=2) | Q(status=-2))) |
#                                      Q(target_member=mm) & (Q(status=0) | Q(status=1) | Q(status=-1)),
#                                      ~Q(creator=user)).count()
#     return count
#
#
# def get_user_invs(user, group_name=None):
#     if group_name:
#         invs = Link.objects.filter(creator=user, group__group_name__iexact=group_name).order_by('-created_time')
#     else:
#         invs = Link.objects.filter(creator=user).order_by('-created_time')
#     return invs
#
#
# def get_user_ego_graph(user, groupid):
#     ls = Link.objects.filter(group__id=groupid, creator=user)
#
#     gms, nodes, links = [], [], []
#
#     self = GroupMember.objects.get(group__id=groupid, user=user)
#     nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
#                   'self': True, 'group': 0})
#
#     if ls.count() != 0:
#
#         for link in ls:
#
#             if link.source_member not in gms and link.source_member != self:
#                 gms.append(link.source_member)
#             if link.target_member not in gms and link.target_member != self:
#                 gms.append(link.target_member)
#
#         for gm in gms:
#             nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
#                           'self': False, 'group': random.randint(1, 4)})
#
#         for link in ls:
#             links.append({'id': link.id, 'source': link.source_member.id, 'target': link.target_member.id,
#                           'status': link.status, 'value': 1, 'group': link.group.id})
#
#     return {"nodes": nodes, "links": links}
#
#
# def get_user_global_graph(user, groupid):
#
#     # Todo: status should =3
#     ls = Link.objects.filter(group__id=groupid)
#
#     nodes, links = [], []
#
#     self = GroupMember.objects.get(group__id=groupid, user=user)
#     nodes.append({'id': self.id, 'userid': self.user.id, 'name': self.member_name,
#                   'self': True, 'group': 0})
#
#     gms = GroupMember.objects.filter(group__id=groupid).exclude(user=user)
#     for gm in gms:
#         nodes.append({'id': gm.id, 'userid': (-1 if gm.user is None else gm.user.id), 'name': gm.member_name,
#                       'self': False, 'group': random.randint(1, 4)})
#
#     if ls.count() != 0:
#
#         G = global_graph(gms, ls, user)
#
#         for s, t, d in G.edges_iter(data='created'):
#             links.append({'source': s.id, 'target': t.id, 'status': d, 'value': 1})
#
#     return {"nodes": nodes, "links": links}
#
#
# def get_user_global_map(user, groupid):
#
#     # Todo: status should =3
#     ls = Link.objects.filter(group__id=groupid)
#     gms = GroupMember.objects.filter(group__id=groupid)
#     my_member = gms.get(group__id=groupid, user=user)
#
#     G = global_graph(gms, ls, user)
#
#     GMap = nx.Graph()
#
#     for gm in gms:
#         if gm.user is not None:
#             g_l = gm.user.extra.location
#             if g_l is not None:
#                 if not GMap.has_node(g_l):
#                     GMap.add_node(g_l, weight=1, friends=0)
#                 else:
#                     GMap.node[g_l]['weight'] += 1
#
#     for friend in G.neighbors(my_member):
#         if friend.user is not None:
#             f_l = friend.user.extra.location
#             if f_l is not None:
#                 GMap.node[f_l]['friends'] += 1
#
#     if user.extra.location is not None:
#         GMap.node[user.extra.location]['self'] = True
#
#     # print GMap.nodes(data=True)
#
#     for link in ls:
#         if link.source_member.user is not None and link.target_member.user is not None:
#             s_l = link.source_member.user.extra.location
#             t_l = link.target_member.user.extra.location
#             if s_l is not None and t_l is not None and s_l != t_l:
#                 if not GMap.has_edge(s_l, t_l):
#                     GMap.add_edge(s_l, t_l)
#
#     # print GMap.edges(data=True)
#
#     nodes, links = [], []
#
#     for (node, d) in GMap.nodes(data=True):
#         # print d
#         country, city = node.split('-')
#         nodes.append({"name": city, "value": CITIES_TABLE[country][city][-1::-1] + [d['weight'], d['friends']],
#                       "self": True if d.has_key('self') else False})
#
#     # print nodes
#
#     for (s, t) in GMap.edges():
#         s_country, s_city = s.split('-')
#         t_country, t_city = t.split('-')
#         links.append({"source": s_city, "target": t_city})
#
#     # print links
#
#     return {"nodes": nodes, "links": links}
#
#
# def get_user_global_info(user, groupid):
#     return graph_analyzer(user, groupid)
#
#
# def get_group_joined_num(group):
#     total = GroupMember.objects.filter(group=group).count()
#
#     joined = GroupMember.objects.filter(group=group, is_joined=True).count()
#
#     return str(joined) + '/' + str(total)
#
#
# def get_user_joined(user, group):
#     return GroupMember.objects.filter(user=user, group=group, is_joined=True).exists()
#
#
# def get_user_join_status(request, user, group):
#
#     join_failed = request.session.get('join_failed')
#     if join_failed:
#         del request.session['join_failed']
#
#     joined = GroupMember.objects.filter(user=user, group=group, is_joined=True).exists()
#
#     requested = MemberRequest.objects.filter(user=user, group=group, is_valid=True).exists()
#
#     if joined:
#         return 1
#     elif join_failed:
#         return -2
#     elif requested:
#         return -1
#     else:
#         return 0
#
#
# ########################################################################
#
#
# def update_profile(request, user, first_name, last_name, birth, sex, country, city, institution):
#     try:
#         user.first_name = first_name
#         user.last_name = last_name
#
#         ue = Extra.objects.get(user=user)
#         ue.sex = sex
#         ue.birth = datetime.datetime.strptime(birth, '%Y/%m/%d').date()
#         ue.location = country + '-' + city
#         ue.institution = institution
#         user.save()
#         ue.save()
#
#     except Exception, e:
#         # print 'Profile update failed: ', e
#         logger.error(logger_join('Update', get_session_id(request), 'failed', e=e))
#         return -1
#     logger.info(logger_join('Update', get_session_id(request)))
#     return 0
#
#
# ########################################################################
#
#
# def create_group(request, user, name, maxsize, identifier, gtype):
#     now = timezone.now()
#
#     # Todo: group validate fix
#     if group_name_existed(name) or maxsize > GROUP_MAXSIZE or user.extra.credits < GROUP_CREATED_CREDITS_COST:
#         return -1
#     try:
#
#         g = Group(group_name=name,
#                   creator=user,
#                   type=gtype,
#                   maxsize=maxsize,
#                   identifier=identifier,
#                   created_time=now,
#                   deprecated=False)
#         g.save()
#
#         m = GroupMember(group=g,
#                         user=user,
#                         member_name=get_user_name(user),
#                         token="creator",
#                         is_creator=True,
#                         is_joined=True,
#                         created_time=now,
#                         joined_time=now)
#
#         user.extra.credits -= GROUP_CREATED_CREDITS_COST
#
#         c = Credits(user=user,
#                     action=-GROUP_CREATED_CREDITS_COST,
#                     timestamp=now)
#
#         m.save()
#         user.extra.save()
#         c.save()
#
#     except Exception, e:
#
#         # Todo: ????fix
#         logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
#         return -1
#
#     # create dummy members
#     # create_dummy_members(g, u, 20)
#     #
#     # # create dummy links
#     # create_dummy_links(g, u, now)
#     logger.info(logger_join('Create', get_session_id(request), gid=g.id))
#     return 0
#
#
# def group_recommender(user):
#     gms = GroupMember.objects.filter(member_name=get_user_name(user), is_joined=False)
#
#     sug = [gm.group for gm in gms]
#
#     return sug
#
#
# ########################################################################
#
# # Todo: token multiple check, and fix same token
# def create_group_member(request, group, name, identifier, user=None):
#     now = timezone.now()
#
#     if GroupMember.objects.filter(member_name=name, group=group).exists():
#         return -1
#
#     try:
#         m = GroupMember(group=group,
#                         user=user,
#                         member_name=name,
#                         token=identifier,
#                         is_creator=False,
#                         is_joined=False,
#                         created_time=now)
#         m.save()
#     except Exception, e:
#         # print 'Group member create: ', e
#         logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
#         return None
#     logger.info(logger_join('Create', get_session_id(request), mid=m.id))
#     return m
#
#
# def member_join(request, user, group, identifier):
#     now = timezone.now()
#     try:
#         m = GroupMember.objects.get((Q(member_name=get_user_name(user)) | Q(member_name=user.username)),
#                                     group=group, token=identifier)
#         m.is_joined = True
#         m.user = user
#         m.joined_time = now
#         m.save()
#     except Exception, e:
#         logger.error(logger_join('Join', get_session_id(request), 'failed', e=e))
#         return -1
#
#     logger.info(logger_join('Join', get_session_id(request), mid=m.id))
#     return 0
#
#
# def member_recommender(user, groupid):
#     if groupid < 0:
#         return None
#     gmout = []
#     gmin = []
#     ls = Link.objects.filter(group__id=groupid, creator=user)
#
#     for l in ls:
#         if l.source_member not in gmin or l.target_member not in gmin:
#             gmin.append(l.source_member)
#             gmin.append(l.target_member)
#
#     for gm in GroupMember.objects.filter(group__id=groupid).exclude(user=user).order_by('-is_joined'):
#         if gm not in gmin:
#             gmout.append(gm)
#
#     return gmout
#
#
# ########################################################################
#
# # Todo: logger and security
# def link_confirm(request, user, linkid):
#     link = get_object_or_404(Link, id=linkid)
#
#     gm = GroupMember.objects.get(user=user, group=link.group)
#
#     if gm is not None:
#         now = timezone.now()
#         link.confirmed_time = now
#
#         if link.source_member == gm:
#             link.status = SOURCE_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]
#
#         elif link.target_member == gm:
#             link.status = TARGET_LINK_CONFIRM_STATUS_TRANSITION_TABLE[link.status]
#
#         else:
#             logger.info(logger_join('Confirm', get_session_id(request), 'failed', lid=linkid))
#             return -1
#         link.save()
#         logger.info(logger_join('Confirm', get_session_id(request), lid=linkid))
#         return 0
#     else:
#         logger.info(logger_join('Confirm', get_session_id(request), 'failed', lid=linkid))
#         return -1
#
#
# def link_reject(request, user, linkid):
#     link = get_object_or_404(Link, id=linkid)
#
#     gm = GroupMember.objects.get(user=user, group=link.group)
#
#     if gm is not None:
#         now = timezone.now()
#         link.confirmed_time = now
#
#         if link.source_member == gm:
#             link.status = SOURCE_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]
#
#         elif link.target_member == gm:
#             link.status = TARGET_LINK_REJECT_STATUS_TRANSITION_TABLE[link.status]
#
#         else:
#             logger.info(logger_join('Reject', get_session_id(request), 'failed', lid=linkid))
#             return -1
#
#         link.save()
#         logger.info(logger_join('Reject', get_session_id(request), lid=linkid))
#         return 0
#     else:
#         logger.info(logger_join('Reject', get_session_id(request), 'failed', lid=linkid))
#         return -1
#
#
# def update_links(request, new_links, groupid, creator):
#     now = timezone.now()
#
#     old_links = Link.objects.filter(creator=creator, group__id=groupid)
#     linksIndex = {}
#
#     for link in old_links:
#         linksIndex[str(link.source_member.id) + ',' + str(link.target_member.id)] = link
#
#     for link in eval(new_links):
#         if link["source"] + ',' + link["target"] in linksIndex:
#             linksIndex[link["source"] + ',' + link["target"]] = 0
#         elif link["target"] + ',' + link["source"] in linksIndex:
#             linksIndex[link["target"] + ',' + link["source"]] = 0
#         else:
#             linksIndex[link["source"] + ',' + link["target"]] = 1
#
#     my_member = GroupMember.objects.get(group__id=groupid, user=creator)
#
#     for k, v in linksIndex.items():
#         if v is 0:
#             continue
#         elif v is 1:
#             try:
#                 source = int(k.split(',')[0])
#                 target = int(k.split(',')[1])
#
#                 # link safety check
#                 if source == my_member.id:
#                     if not GroupMember.objects.get(id=target, group__id=groupid):
#                         continue
#                     else:
#                         status = 1
#                 elif target == my_member.id:
#                     if not GroupMember.objects.get(id=source, group__id=groupid):
#                         continue
#                     else:
#                         status = 2
#                 else:
#                     if not (GroupMember.objects.get(id=source, group__id=groupid) and
#                             GroupMember.objects.get(id=source, group__id=groupid)):
#                         continue
#                     else:
#                         status = 0
#
#                 l = Link(creator=creator,
#                          source_member_id=source,
#                          target_member_id=target,
#                          group_id=groupid,
#                          status=status,
#                          created_time=now)
#                 l.save()
#
#             except Exception, e:
#                 logger.error(logger_join('Update', get_session_id(request), 'failed', e=e))
#                 return -1
#         else:
#             v.delete()
#
#     logger.info(logger_join('Update', get_session_id(request), gid=groupid))
#     return 0
#
#
# ########################################################################
#
#
# def create_dummy_members(group, u, num):
#     for i in range(num):
#         if u.username != 'test' + str(i):
#             create_group_member(group, 'test' + str(i), 'test' + str(i) + '@123.com')
#
#
# def create_dummy_links(group, user, now):
#     num = GroupMember.objects.filter(group=group).count()
#     G = nx.barabasi_albert_graph(num, 2)
#
#     i = 0
#     for node in G.nodes():
#         if node == 0:
#             G.node[node]['name'] = user.username
#         else:
#             G.node[node]['name'] = 'test' + str(i)
#             i += 1
#
#     for (f, t) in G.edges():
#         link = Link(creator=user,
#                     source_member=GroupMember.objects.get(member_name=G.node[f]['name'], group=group),
#                     target_member=GroupMember.objects.get(member_name=G.node[t]['name'], group=group),
#                     group=group,
#                     status=0,
#                     created_time=now)
#         link.save()
#
#
# def global_graph(nodes, links, user):
#     G = nx.Graph()
#
#     # all members are calculated as nodes or only linked member are nodes
#     for node in nodes:
#         G.add_node(node)
#
#     for link in links:
#         if not G.has_edge(link.source_member, link.target_member):
#             if link.creator == user:
#                 G.add_edge(link.source_member, link.target_member, weight=1, created=True)
#             else:
#                 G.add_edge(link.source_member, link.target_member, weight=1)
#         else:
#             if link.creator == user:
#                 G[link.source_member][link.target_member]['weight'] += 1
#                 G[link.source_member][link.target_member]['created'] = True
#             else:
#                 G[link.source_member][link.target_member]['weight'] += 1
#
#     return G
#
#
# # Todo: link status should be 3
# def graph_analyzer(user, groupid):
#     nodes = GroupMember.objects.filter(group__id=groupid)
#     links = Link.objects.filter(group__id=groupid)
#     my_member = nodes.get(user=user)
#
#     G = global_graph(nodes, links, user)
#
#     # print my_member
#
#     # print G.edges(data=True)
#
#     distribution = {k: v / float(G.number_of_nodes()) for k, v in dict(Counter(G.degree().values())).items()}
#
#     # print distribution, dict(Counter(G.degree().values()))
#
#     # distribution = {str(k): v for k, v in nx.degree_centrality(G)}
#
#     top = sorted(G.degree().items(), key=lambda x: x[1], reverse=True)
#     top3 = top[0:3]
#
#     myRank = top.index((my_member, G.degree(my_member))) + 1
#
#     # print top3, myRank
#
#     myGraph = links.filter(creator=user).count()
#
#     cover = myGraph / float(G.number_of_edges()) if not G.number_of_edges() == 0 else 0
#
#     # print cover
#
#     average_degree = 2 * G.number_of_edges() / G.number_of_nodes()
#
#     # If the network is not connected,
#     # return -1
#     if nx.is_connected(G) and G.number_of_nodes() > 1:
#         average_distance = nx.average_shortest_path_length(G)
#     else:
#         average_distance = -1
#
#     print average_degree, average_distance
#
#     friends = G.neighbors(my_member)
#     friends = [(friend, G[friend][my_member]['weight']) for friend in friends]
#     friends = sorted(friends, key=lambda x: x[1], reverse=True)
#
#     # print friends
#     # print friends[0][0].id
#     if len(friends) > 0:
#         bestfriend = friends[0][0]
#         bf_ratio = friends[0][1] / float(G.number_of_nodes())
#     else:
#         bestfriend = None
#         bf_ratio = 0
#
#     # Todo: ratio not correct
#     links_of_me = links.filter(Q(source_member=my_member) | Q(target_member=my_member)).exclude(creator=user) \
#         .values('creator').annotate(count=Count('pk')).order_by('-count')
#
#     # print links_of_me
#     if len(links_of_me) != 0:
#         heart = GroupMember.objects.get(user__id=links_of_me[0]['creator'], group__id=groupid)
#         heart_count = links_of_me[0]['count']
#     else:
#         heart = None
#         heart_count = None
#
#     return {'distribution': json.dumps(distribution), 'top3': top3, 'my_rank': myRank,
#             'average_degree': average_degree, 'average_distance': average_distance,
#             'cover': cover,
#             'bestfriend': bestfriend, 'bf_ratio': bf_ratio,
#             'heart': heart, 'heart_count': heart_count}