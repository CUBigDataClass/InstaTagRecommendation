import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-caption-generator',
  templateUrl: './caption-generator.component.html',
  styleUrls: ['./caption-generator.component.css']
})
export class CaptionGeneratorComponent implements OnInit {

  caption!: File;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
  }


  OnImageChange(event: any){
    this.caption= event.target.files[0];
  }
  OnCaptionSubmit(){
    const uploadData =new FormData();
    uploadData.append('caption',this.caption);

    this.http.post('http://127.0.0.1:8000/files/',uploadData).subscribe(
      data => console.log(data),
      error => console.log(error)
    );
  }

}
