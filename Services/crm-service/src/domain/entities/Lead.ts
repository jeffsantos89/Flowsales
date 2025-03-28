export class Lead {
  constructor(
    public id: string,
    public name: string,
    public email: string,
    public score: number = 0
  ) {}
}
