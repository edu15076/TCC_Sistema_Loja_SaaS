package Entidade;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

import jakarta.persistence.*;

@Entity
@Table(name = "contratante")
public class Contratante extends Pessoa implements Serializable {
    private String username;
    private String senha;
    private String cnpj;
    
    @OneToOne(mappedBy = "contratante")
    private Loja loja;
    
    @OneToMany(mappedBy = "contratante")
    private List<Cartao> cartoes;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getSenha() {
        return senha;
    }

    public void setSenha(String senha) {
        this.senha = senha;
    }

    public String getCnpj() {
        return cnpj;
    }

    public void setCnpj(String cnpj) {
        this.cnpj = cnpj;
    }

    public Loja getLoja() {
        return loja;
    }

    public void setLoja(Loja loja) {
        this.loja = loja;
    }

    public List<Cartao> getCartoes() {
        return cartoes;
    }

    public void setCartoes(List<Cartao> cartoes) {
        this.cartoes = cartoes;
    }

    public String toString() {
        return String.join("\n",
                "ID: " + this.getId(),
                "Username: " + this.getUsername(),
                "CNPJ: " + this.getCnpj(),
                "Nome: " + this.getNome(),
                "Sobrenome: " + this.getSobrenome(),
                "Data de Nascimento: " + this.getNascimento(),
                "Email: " + this.getEmail(),
                "Telefone: " + this.getTelefone()
        );
    }
}
