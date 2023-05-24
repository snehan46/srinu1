import { Component, OnInit } from '@angular/core';
import { AuthService } from '../_services/auth.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  public periodicity!: string;
  public timePeriod!: string;
  public csvFile!: File;
  public mae!: number;
  public rmse!: number;
  public showProfile = false;

  
  constructor(private auth:AuthService ,private http: HttpClient) { }
  user = {localId:"someid",displayName:"somename",email:"somemail"};
  ngOnInit(): void {
    this.auth.canAccess();
    if (this.auth.isAuthenticated()) {
       
      
        this.auth.detail().subscribe({
          next:data=>{
              this.user.localId = data.users[0].localId;
              this.user.displayName = data.users[0].displayName;
              this.user.email=data.users[0].email;
          }
        })
    }
  }

  onFileSelected(event: any) {
    this.csvFile = event.target.files[0];
  }

  onSubmit() {
    if (!this.csvFile || !this.periodicity || !this.timePeriod) {
      alert('Please fill all the fields.');
      return;
    }
    alert('Form submitted!');

    const formData = new FormData();
    formData.append('csvFile', this.csvFile);
    formData.append('periodicity', this.periodicity);
    formData.append('timePeriod', this.timePeriod);
    this.http.post('http://localhost:5000/forecast', formData).subscribe(
      (response: any) => {
        console.log(response);
        this.mae = response.mae;
        this.rmse = response.rmse;
      },
      (error) => console.log(error)
    );
  }
  
  showProfilePopup() {
    this.showProfile = true;
  }

  hideProfilePopup() {
    this.showProfile = false;
  }
}

