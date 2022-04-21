import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CaptionGeneratorComponent } from './caption-generator/caption-generator.component';
import { HashtagListComponent } from './hashtag-list/hashtag-list.component';
import { TagGeneratorComponent } from './tag-generator/tag-generator.component';

const routes: Routes = [
  { path: 'app-tag-generator', component: TagGeneratorComponent },
  { path: 'app-caption-generator', component: CaptionGeneratorComponent},
  { path: 'app-hashtag-list', component: HashtagListComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
