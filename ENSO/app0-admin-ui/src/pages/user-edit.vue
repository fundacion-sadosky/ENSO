<script setup lang="ts">
import { ref, onBeforeMount } from 'vue'
import { platformService } from '/@src/services/platformService'
import { useRoute } from 'vue-router'
import { useHead } from '@vueuse/head'

useHead({
  title: 'User',
})

const theObj = ref({})
const route = useRoute()

const isNew = () => {
  if (route.params.objId == 'new') {
    return true
  }
  return false
}

onBeforeMount(async () => {
  if (!isNew()) {
    const objId = route.params.objId
    let ret = await platformService.getUser(objId)
    theObj.value = ret
  }
})
</script>

<template>
  <SidebarLayout>
    <div class="page-content-inner">
      <VBreadcrumb
        v-if="theObj.id"
        :items="[
          {
            label: 'Home',
            hideLabel: true,
            icon: 'feather:home',
            to: { name: 'home' },
          },
          {
            label: 'Usuarios',
            icon: 'icon-park-outline:peoples',
            to: { name: 'users' },
          },
          {
            label: theObj.firstname + ' ' + theObj.surname,
            to: { name: 'user-edit', params: { objId: theObj.id } },
          },
        ]"
        with-icons
      />
      <VBreadcrumb
        v-if="theObj && !theObj.id"
        :items="[
          {
            label: 'Home',
            hideLabel: true,
            icon: 'feather:home',
            to: { name: 'home' },
          },
          {
            label: 'Usuarios',
            icon: 'icon-park-outline:peoples',
            to: { name: 'users' },
          },
          {
            label: 'Nuevo',
          },
        ]"
        with-icons
      />
      <!--Edit Profile-->
      <div class="account-wrapper">
        <div class="columns">
          <!--Navigation-->
          <div v-if="theObj" class="column is-4">
            <div class="account-box is-navigation">
              <template v-if="isNew()">
                <VBlock title="Nuevo Usuario" subtitle="Ingrese detalles" center>
                  <template #icon>
                    <VAvatar initials="NU" size="large" />
                  </template>
                </VBlock>
              </template>
              <template v-if="!isNew() && theObj.firstname">
                <VBlock :title="theObj.firstname + ' ' + theObj.surname" subtitle="User" center>
                  <template #icon>
                    <Logo :image="theObj.image" :name1="theObj.firstname" :name2="theObj.surname" size="large" />
                  </template>
                </VBlock>
              </template>

              <div v-if="!isNew() && theObj.id" class="account-menu">
                <RouterLink :to="{ name: 'user-edit', params: { objId: theObj.id } }" class="account-menu-item">
                  <i aria-hidden="true" class="lnil lnil-user-alt"></i>
                  <span>General</span>
                  <span class="end">
                    <i aria-hidden="true" class="fas fa-arrow-right"></i>
                  </span>
                </RouterLink>
              </div>
            </div>
          </div>
          <div class="column is-8">
            <UserForm />
          </div>
        </div>
      </div>
    </div>
  </SidebarLayout>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';

.is-navbar {
  .account-wrapper {
    margin-top: 30px;
  }
}

.account-wrapper {
  padding-bottom: 60px;

  .account-box {
    @include vuero-s-card;

    &.is-navigation {
      .media-flex-center {
        padding-bottom: 20px;

        .flex-meta {
          span {
            &:first-child {
              font-size: 1.3rem;
            }
          }
        }
      }

      .account-menu {
        .account-menu-item {
          display: flex;
          align-items: center;
          padding: 12px 16px;
          border: 1px solid transparent;
          border-radius: 8px;
          margin-bottom: 5px;
          transition: all 0.3s; // transition-all test

          &.router-link-exact-active {
            box-shadow: var(--light-box-shadow);
            border-color: var(--fade-grey-dark-3);

            span,
            i {
              color: var(--primary);
            }

            .end {
              display: block;
            }
          }

          &:not(.router-link-exact-active) {
            &:hover {
              background: var(--fade-grey-light-3);
            }
          }

          i {
            margin-right: 8px;
            font-size: 1.1rem;
            color: var(--light-text);

            &.fas,
            .fal,
            .far {
              font-size: 0.9rem;
            }
          }

          span {
            font-family: var(--font-alt);
            font-size: 0.95rem;
            color: var(--dark-text);
          }

          .end {
            margin-left: auto;
            display: none;
          }
        }
      }
    }

    &.is-form {
      padding: 0;

      &.is-footerless {
        padding-bottom: 20px;
      }

      .form-head,
      .form-foot {
        padding: 12px 20px;

        .form-head-inner,
        .form-foot-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
      }

      .form-head {
        border-bottom: 1px solid var(--fade-grey-dark-3);
        transition: all 0.3s; // transition-all test

        &.is-stuck {
          background: var(--white);
          padding-right: 80px;
          border-left: 1px solid var(--fade-grey-dark-3);
        }

        .left {
          h3 {
            font-family: var(--font-alt);
            font-size: 1.2rem;
            line-height: 1.3;
          }

          p {
            font-size: 0.95rem;
          }
        }
      }

      .form-foot {
        border-top: 1px solid var(--fade-grey-dark-3);
      }

      .form-body {
        padding: 20px;

        .fieldset {
          padding: 20px 0;
          max-width: 480px;
          margin: 0 auto;

          .fieldset-heading {
            margin-bottom: 20px;

            h4 {
              font-family: var(--font-alt);
              font-weight: 600;
              font-size: 1rem;
            }

            p {
              font-size: 0.9rem;
            }
          }

          .v-avatar {
            position: relative;
            display: block;
            margin: 0 auto;

            .edit-button {
              position: absolute;
              bottom: 0;
              right: 0;
            }
          }

          .setting-list {
            .setting-form {
              text-align: center;

              .filepond-profile-wrap {
                margin: 0 auto 10px !important;
              }
            }

            .setting-item {
              display: flex;
              align-items: center;
              margin-bottom: 24px;

              .icon-wrap {
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 50px;
                min-width: 50px;
                height: 50px;
                border-radius: var(--radius-rounded);
                background: var(--fade-grey-light-2);
                border: 1px solid var(--fade-grey-dark-3);
                color: var(--light-text);

                &.has-img {
                  border-color: var(--primary);

                  img {
                    width: 36px;
                    min-width: 36px;
                    height: 36px;
                  }
                }

                i {
                  font-size: 1.4rem;
                }
              }

              img {
                display: block;
                width: 50px;
                min-width: 50px;
                height: 50px;
                border-radius: var(--radius-rounded);
                border: 1px solid transparent;
              }

              .meta {
                margin-left: 10px;

                > span {
                  font-family: var(--font);
                  display: block;

                  &:first-child {
                    font-family: var(--font-alt);
                    font-weight: 600;
                    color: var(--dark-text);
                    font-size: 0.9rem;
                  }

                  &:nth-child(2),
                  &:nth-child(3) {
                    font-size: 0.85rem;
                    color: var(--light-text);

                    i {
                      position: relative;
                      top: -2px;
                      font-size: 4px;
                      margin: 0 6px;
                    }
                  }

                  &:nth-child(3) {
                    color: var(--primary);
                  }

                  span {
                    display: inline-block;
                  }
                }
              }

              .end {
                margin-left: auto;
              }
            }
          }
        }
      }
    }
  }
}

.is-dark {
  .account-wrapper {
    .account-box {
      @include vuero-card--dark;

      &.is-navigation {
        .account-menu {
          .account-menu-item {
            &.router-link-exact-active {
              background: var(--dark-sidebar-light-8);
              border-color: var(--dark-sidebar-light-12);

              i,
              span {
                color: var(--primary);
              }
            }

            &:not(.router-link-exact-active) {
              &:hover {
                background: var(--dark-sidebar-light-10);
              }
            }

            span {
              color: var(--dark-dark-text);
            }
          }
        }
      }

      &.is-form {
        .form-head,
        .form-foot {
          border-color: var(--dark-sidebar-light-12);
        }

        .form-head {
          &.is-stuck {
            background: var(--dark-sidebar);
            border-color: var(--dark-sidebar-light-6);
          }

          .left {
            h3 {
              color: var(--dark-dark-text);
            }
          }
        }

        .form-body {
          .fieldset {
            .fieldset-heading {
              h4 {
                color: var(--dark-dark-text);
              }
            }

            .setting-list {
              .setting-item {
                > img,
                > .icon-wrap,
                > .icon-wrap img {
                  border-color: var(--dark-sidebar-light-12);
                }

                > .icon-wrap {
                  background: var(--dark-sidebar-light-2);
                }

                .meta {
                  > span {
                    &:nth-child(3) {
                      color: var(--primary);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>
